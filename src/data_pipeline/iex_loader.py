"""
IEX data loading, standardisation, and merging.

Handles the messy reality of IEX data files: inconsistent column
names, mixed date formats, optional fields, and multiple file layouts
from Kaggle, Mendeley, and Zenodo sources.

All loaders return DataFrames with canonical column names (lowercase,
underscore-separated) and validated block numbers / dates.
"""

from __future__ import annotations

import glob
import logging
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Union

import numpy as np
import pandas as pd

from indian_power_market.src.data_pipeline.iex_schema import (
    BLOCKS_PER_DAY,
    CERC_PRICE_CAP,
    CERC_PRICE_FLOOR,
    blocks_to_hours,
    blocks_to_sessions,
    validate_dataframe,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Column mapping
# ---------------------------------------------------------------------------

#: Maps every known raw column variant (lowered, stripped) to the
#: canonical name used internally.
_COLUMN_ALIASES: Dict[str, str] = {
    # --- date / time ---
    "date": "date",
    "delivery date": "date",
    "trade date": "date",
    "trading date": "date",
    # --- block ---
    "block no": "block_no",
    "block no.": "block_no",
    "block_no": "block_no",
    "block number": "block_no",
    "block": "block_no",
    "time block": "block_no",
    "timeblock": "block_no",
    "time block no.": "block_no",
    "time block no": "block_no",
    # --- hour ---
    "hour": "hour",
    "hours": "hour",
    # --- session ---
    "session": "session_id",
    "session_id": "session_id",
    "session id": "session_id",
    "session no": "session_id",
    "session no.": "session_id",
    # --- purchase bid ---
    "purchase bid (mw)": "purchase_bid_mw",
    "purchase bid(mw)": "purchase_bid_mw",
    "purchase_bid_mw": "purchase_bid_mw",
    "purchase bid": "purchase_bid_mw",
    "total purchase bid (mw)": "purchase_bid_mw",
    "buy bid (mw)": "purchase_bid_mw",
    "buy bid": "purchase_bid_mw",
    "demand bid (mw)": "purchase_bid_mw",
    # --- sell bid ---
    "sell bid (mw)": "sell_bid_mw",
    "sell bid(mw)": "sell_bid_mw",
    "sell_bid_mw": "sell_bid_mw",
    "sell bid": "sell_bid_mw",
    "total sell bid (mw)": "sell_bid_mw",
    "supply bid (mw)": "sell_bid_mw",
    "supply bid": "sell_bid_mw",
    # --- MCV ---
    "mcv (mw)": "mcv_mw",
    "mcv(mw)": "mcv_mw",
    "mcv_mw": "mcv_mw",
    "mcv": "mcv_mw",
    "market clearing volume (mw)": "mcv_mw",
    "market clearing volume": "mcv_mw",
    "cleared volume (mw)": "mcv_mw",
    # --- MCP ---
    "mcp (rs/mwh)": "mcp",
    "mcp(rs/mwh)": "mcp",
    "mcp (rs/kwh)": "mcp_kwh",
    "mcp(rs/kwh)": "mcp_kwh",
    "mcp": "mcp",
    "mcp_rs_mwh": "mcp",
    "mcp_rs_kwh": "mcp_kwh",
    "market clearing price (rs/mwh)": "mcp",
    "market clearing price": "mcp",
    "price (rs/mwh)": "mcp",
    "price": "mcp",
    # --- DAM prefix ---
    "dam mcp (rs/mwh)": "dam_mcp",
    "dam_mcp": "dam_mcp",
    "dam price": "dam_mcp",
    # --- RTM prefix ---
    "rtm mcp (rs/mwh)": "rtm_mcp",
    "rtm_mcp": "rtm_mcp",
    "rtm price": "rtm_mcp",
}


def _normalise_colname(raw: str) -> str:
    """Lower-case, collapse whitespace, strip parentheses whitespace."""
    s = raw.strip().lower()
    # Collapse multiple spaces
    s = re.sub(r"\s+", " ", s)
    return s


def standardize_columns(
    df: pd.DataFrame,
    market_type: str = "dam",
) -> pd.DataFrame:
    """Map raw IEX column names to canonical lowercase_underscore names.

    Parameters
    ----------
    df : pd.DataFrame
        Raw DataFrame as read from CSV / Excel.
    market_type : str
        ``"dam"`` or ``"rtm"``.  Used to prefix the MCP column
        when both markets are present (e.g. ``"dam_mcp"``).

    Returns
    -------
    pd.DataFrame
        DataFrame with standardised column names.  Unknown columns
        are preserved as-is (lowered + underscored).
    """
    market_type = market_type.strip().lower()
    if market_type not in ("dam", "rtm"):
        raise ValueError(f"market_type must be 'dam' or 'rtm', got '{market_type}'")

    rename_map: Dict[str, str] = {}
    for raw_col in df.columns:
        normed = _normalise_colname(str(raw_col))
        if normed in _COLUMN_ALIASES:
            canonical = _COLUMN_ALIASES[normed]
            rename_map[raw_col] = canonical
        else:
            # Fallback: lower + underscores
            rename_map[raw_col] = re.sub(r"[^a-z0-9]+", "_", normed).strip("_")

    out = df.rename(columns=rename_map)

    # --- Convert MCP from Rs/kWh to Rs/MWh if needed ---
    if "mcp_kwh" in out.columns and "mcp" not in out.columns:
        out["mcp"] = out["mcp_kwh"] * 1_000.0
        out.drop(columns=["mcp_kwh"], inplace=True)
        logger.info("Converted MCP from Rs/kWh to Rs/MWh.")

    # --- Prefix MCP for the given market ---
    if "mcp" in out.columns and market_type in ("dam", "rtm"):
        prefixed = f"{market_type}_mcp"
        if prefixed not in out.columns:
            out.rename(columns={"mcp": prefixed}, inplace=True)

    return out


# ---------------------------------------------------------------------------
# Kaggle DAM loader
# ---------------------------------------------------------------------------

def load_dam_from_kaggle(
    path: Union[str, Path],
    *,
    validate: bool = True,
) -> pd.DataFrame:
    """Load the Kaggle DAM dataset (CSV or Excel) into a clean DataFrame.

    Handles the common Kaggle IEX DAM layouts:
    * Date | Block No | Purchase Bid (MW) | Sell Bid (MW) | MCV (MW) | MCP (Rs/MWh)
    * May include ``Time Block`` instead of ``Block No``
    * May have ``MCP (Rs/kWh)`` which gets auto-converted

    Parameters
    ----------
    path : str | Path
        Path to a ``.csv`` or ``.xlsx`` / ``.xls`` file.
    validate : bool
        If ``True``, run :func:`validate_dataframe` and log warnings.

    Returns
    -------
    pd.DataFrame
        Columns: ``date, block_no, hour, session_id, purchase_bid_mw,
        sell_bid_mw, mcv_mw, dam_mcp`` plus any extra original columns.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"DAM file not found: {path}")

    # --- Read ---
    if path.suffix.lower() in (".xlsx", ".xls"):
        raw = pd.read_excel(path)
    else:
        raw = pd.read_csv(path, low_memory=False)

    logger.info("Read %d rows × %d cols from %s", len(raw), len(raw.columns), path)

    # --- Standardise ---
    df = standardize_columns(raw, market_type="dam")

    # --- Parse date ---
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce").dt.date

    # --- Infer block_no if missing ---
    if "block_no" not in df.columns:
        if "hour" in df.columns:
            # Derive from hour (assuming rows are sorted within each date)
            df["block_no"] = (df["hour"].astype(float) * 4 + 1).astype(int)
            logger.info("Inferred block_no from hour column.")
        elif "date" in df.columns:
            # Assume rows are in block order within each date
            df["block_no"] = df.groupby("date").cumcount() + 1
            logger.info("Inferred block_no from row order within date groups.")
    else:
        df["block_no"] = pd.to_numeric(df["block_no"], errors="coerce").astype("Int64")

    # --- Derive hour and session_id ---
    if "block_no" in df.columns:
        valid_blocks = df["block_no"].notna()
        block_arr = df.loc[valid_blocks, "block_no"].values.astype(np.int64)
        df.loc[valid_blocks, "hour"] = blocks_to_hours(block_arr)
        df.loc[valid_blocks, "session_id"] = blocks_to_sessions(block_arr)

    # --- Coerce numeric volume / price columns ---
    for col in ("purchase_bid_mw", "sell_bid_mw", "mcv_mw", "dam_mcp"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # --- Validate ---
    if validate and "dam_mcp" in df.columns:
        validate_dataframe(df, price_col="dam_mcp")

    df = df.sort_values(["date", "block_no"]).reset_index(drop=True)
    logger.info("DAM DataFrame ready: %d rows", len(df))
    return df


# ---------------------------------------------------------------------------
# RTM loader (for future real data)
# ---------------------------------------------------------------------------

def load_rtm_from_csv(
    path: Union[str, Path],
    *,
    validate: bool = True,
) -> pd.DataFrame:
    """Load an RTM CSV into a standardised DataFrame.

    Parameters
    ----------
    path : str | Path
        Path to RTM CSV file.
    validate : bool
        If ``True``, run :func:`validate_dataframe` and log warnings.

    Returns
    -------
    pd.DataFrame
        Columns include ``date, block_no, hour, session_id, rtm_mcp``
        and volume columns when available.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"RTM file not found: {path}")

    raw = pd.read_csv(path, low_memory=False)
    logger.info("Read %d rows × %d cols from %s", len(raw), len(raw.columns), path)

    df = standardize_columns(raw, market_type="rtm")

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce").dt.date

    if "block_no" in df.columns:
        df["block_no"] = pd.to_numeric(df["block_no"], errors="coerce").astype("Int64")
        valid = df["block_no"].notna()
        block_arr = df.loc[valid, "block_no"].values.astype(np.int64)
        df.loc[valid, "hour"] = blocks_to_hours(block_arr)
        df.loc[valid, "session_id"] = blocks_to_sessions(block_arr)

    for col in ("purchase_bid_mw", "sell_bid_mw", "mcv_mw", "rtm_mcp"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if validate and "rtm_mcp" in df.columns:
        validate_dataframe(df, price_col="rtm_mcp")

    df = df.sort_values(["date", "block_no"]).reset_index(drop=True)
    logger.info("RTM DataFrame ready: %d rows", len(df))
    return df


# ---------------------------------------------------------------------------
# Mendeley demand / generation loader
# ---------------------------------------------------------------------------

def load_mendeley_demand(
    directory: Union[str, Path],
    *,
    file_pattern: str = "*.xlsx",
) -> pd.DataFrame:
    """Load hourly demand / solar / wind Excel files from Mendeley.

    Expects one or more Excel files with columns like
    ``Date | Hour | Demand (MW) | Solar (MW) | Wind (MW)``.

    Parameters
    ----------
    directory : str | Path
        Folder containing the Excel files.
    file_pattern : str
        Glob pattern for matching files.

    Returns
    -------
    pd.DataFrame
        Combined DataFrame sorted by date and hour, with column names
        standardised.
    """
    directory = Path(directory)
    if not directory.is_dir():
        raise NotADirectoryError(f"Mendeley directory not found: {directory}")

    files = sorted(directory.glob(file_pattern))
    if not files:
        raise FileNotFoundError(
            f"No files matching '{file_pattern}' in {directory}"
        )

    frames: List[pd.DataFrame] = []
    for fp in files:
        try:
            tmp = pd.read_excel(fp)
            # Standardise column names (lowered + underscored)
            tmp.columns = [
                re.sub(r"[^a-z0-9]+", "_", c.strip().lower()).strip("_")
                for c in tmp.columns
            ]
            frames.append(tmp)
            logger.info("Read %d rows from %s", len(tmp), fp.name)
        except Exception as exc:
            logger.warning("Skipping %s: %s", fp.name, exc)

    if not frames:
        raise RuntimeError("No valid files could be read from Mendeley directory.")

    df = pd.concat(frames, ignore_index=True)

    # Parse date
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce").dt.date

    df = df.sort_values(["date", "hour"] if "hour" in df.columns else ["date"])
    df.reset_index(drop=True, inplace=True)
    logger.info("Mendeley demand DataFrame: %d rows", len(df))
    return df


# ---------------------------------------------------------------------------
# Zenodo weather loader
# ---------------------------------------------------------------------------

def load_zenodo_weather(
    directory: Union[str, Path],
    *,
    file_pattern: str = "*.csv",
    aggregate_to_india: bool = True,
) -> pd.DataFrame:
    """Load state-level daily weather CSVs and aggregate to all-India.

    Parameters
    ----------
    directory : str | Path
        Folder containing per-state CSV files.
    file_pattern : str
        Glob pattern.
    aggregate_to_india : bool
        If ``True``, compute population-weighted or simple mean
        across states to produce a single all-India row per date.

    Returns
    -------
    pd.DataFrame
        Columns: ``date, temperature, humidity, wind_speed, ...``
    """
    directory = Path(directory)
    if not directory.is_dir():
        raise NotADirectoryError(f"Zenodo directory not found: {directory}")

    files = sorted(directory.glob(file_pattern))
    if not files:
        raise FileNotFoundError(
            f"No files matching '{file_pattern}' in {directory}"
        )

    frames: List[pd.DataFrame] = []
    for fp in files:
        try:
            tmp = pd.read_csv(fp, low_memory=False)
            tmp.columns = [
                re.sub(r"[^a-z0-9]+", "_", c.strip().lower()).strip("_")
                for c in tmp.columns
            ]
            # Tag with state derived from filename
            state = fp.stem.replace("_", " ").title()
            tmp["state"] = state
            frames.append(tmp)
        except Exception as exc:
            logger.warning("Skipping %s: %s", fp.name, exc)

    if not frames:
        raise RuntimeError("No valid files read from Zenodo directory.")

    df = pd.concat(frames, ignore_index=True)

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce").dt.date

    if aggregate_to_india:
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        # Remove 'state' grouping — just mean by date
        if "date" in df.columns and numeric_cols:
            df = df.groupby("date", as_index=False)[numeric_cols].mean()
            logger.info("Aggregated to all-India: %d rows", len(df))

    df = df.sort_values("date").reset_index(drop=True)
    return df


# ---------------------------------------------------------------------------
# DAM + RTM merge
# ---------------------------------------------------------------------------

def merge_dam_rtm(
    dam_df: pd.DataFrame,
    rtm_df: pd.DataFrame,
    *,
    validate_alignment: bool = True,
) -> pd.DataFrame:
    """Inner-join DAM and RTM on ``(date, block_no)`` and compute spread.

    Parameters
    ----------
    dam_df : pd.DataFrame
        Must contain ``date, block_no, dam_mcp``.
    rtm_df : pd.DataFrame
        Must contain ``date, block_no, rtm_mcp``.
    validate_alignment : bool
        If ``True``, warn when fewer than 80 % of DAM rows have
        matching RTM rows.

    Returns
    -------
    pd.DataFrame
        Merged DataFrame with additional column ``dam_rtm_spread``
        (= rtm_mcp − dam_mcp).
    """
    for name, required, src_df in [
        ("dam_df", {"date", "block_no", "dam_mcp"}, dam_df),
        ("rtm_df", {"date", "block_no", "rtm_mcp"}, rtm_df),
    ]:
        missing = required - set(src_df.columns)
        if missing:
            raise KeyError(f"{name} is missing columns: {missing}")

    merged = dam_df.merge(
        rtm_df,
        on=["date", "block_no"],
        how="inner",
        suffixes=("_dam", "_rtm"),
    )

    # Compute spread
    merged["dam_rtm_spread"] = merged["rtm_mcp"] - merged["dam_mcp"]

    if validate_alignment:
        pct = len(merged) / max(len(dam_df), 1) * 100
        logger.info(
            "DAM-RTM merge: %d rows (%.1f%% of DAM matched).",
            len(merged),
            pct,
        )
        if pct < 80:
            import warnings

            warnings.warn(
                f"Only {pct:.1f}% of DAM rows matched RTM. Check date/block "
                f"alignment.",
                stacklevel=2,
            )

    merged = merged.sort_values(["date", "block_no"]).reset_index(drop=True)
    return merged
