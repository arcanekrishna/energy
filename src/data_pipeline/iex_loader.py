"""
IEX data loading, standardisation, and merging for Indian electricity markets.

Handles real IEX files, official market snapshots, historical archives,
and Grid-India SCADA generation telemetry:
- DAM_Market Snapshot.xlsx & RTM_Market Snapshot.xlsx (IEX 15-min snapshot exports)
- DAM.xlsx (233,760 blocks of 15-min historical clearing data from 2018-2024)
- DAM.csv (Kaggle/IEX time-series export)
- Electricity Demand, Solar and Wind Generation Data/*.xlsx (Grid-India 5-min SCADA telemetry)
"""

from __future__ import annotations

import glob
import logging
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd

try:
    from src.data_pipeline.iex_schema import (
        BLOCKS_PER_DAY,
        CERC_PRICE_CAP,
        CERC_PRICE_FLOOR,
        blocks_to_hours,
        blocks_to_sessions,
        validate_dataframe,
    )
except ImportError:
    try:
        from indian_power_market.src.data_pipeline.iex_schema import (
            BLOCKS_PER_DAY,
            CERC_PRICE_CAP,
            CERC_PRICE_FLOOR,
            blocks_to_hours,
            blocks_to_sessions,
            validate_dataframe,
        )
    except ImportError:
        from .iex_schema import (
            BLOCKS_PER_DAY,
            CERC_PRICE_CAP,
            CERC_PRICE_FLOOR,
            blocks_to_hours,
            blocks_to_sessions,
            validate_dataframe,
        )

logger = logging.getLogger(__name__)


def load_market_snapshot(
    path: Union[str, Path],
    market_type: str = "dam",
) -> pd.DataFrame:
    """
    Loads official IEX Market Snapshot Excel files (e.g. DAM_Market Snapshot.xlsx,
    RTM_Market Snapshot.xlsx).

    Skips metadata title rows, parses Date and 15-minute Time Blocks, strips summary
    statistic rows (Max/Min/Avg), and standardizes column names.

    Parameters
    ----------
    path : str | Path
        Path to the snapshot Excel file.
    market_type : str, default="dam"
        Either 'dam' or 'rtm'.

    Returns
    -------
    pd.DataFrame
        Standardized DataFrame with columns:
        date, time_block, block_no, hour, session_id,
        purchase_bid_mw, sell_bid_mw, mcv_mw, scheduled_volume_mw, mcp
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Snapshot file not found: {path}")

    # Official IEX snapshots have 4 metadata rows before table header
    df_raw = pd.read_excel(path, skiprows=4)

    # Filter out footer summary statistics rows (where Hour is 'Max (MW)', 'Min (MW)', etc.)
    valid_rows = pd.to_numeric(df_raw["Hour"], errors="coerce").notna()
    df = df_raw[valid_rows].copy()

    # Parse and normalize Date
    df["date"] = pd.to_datetime(df["Date"], dayfirst=True).dt.date

    # Normalize Time Block (e.g., '00:00 - 00:15' -> '00:00-00:15')
    df["time_block"] = df["Time Block"].astype(str).str.replace(" ", "")

    # Derive 1-based block_no (1 to 96) from time_block
    def _parse_time_block_to_block_no(tb: str) -> int:
        try:
            start_str = tb.split("-")[0]
            hh, mm = map(int, start_str.split(":"))
            return (hh * 4) + (mm // 15) + 1
        except Exception:
            return 1

    df["block_no"] = df["time_block"].apply(_parse_time_block_to_block_no)
    df["hour"] = ((df["block_no"] - 1) // 4) + 1
    df["session_id"] = ((df["block_no"] - 1) // 2) + 1

    # Numeric conversions
    prefix = market_type.lower()
    df[f"{prefix}_purchase_bid_mw"] = pd.to_numeric(df["Purchase Bid (MW)"], errors="coerce")
    df[f"{prefix}_sell_bid_mw"] = pd.to_numeric(df["Sell Bid (MW)"], errors="coerce")
    df[f"{prefix}_mcv_mw"] = pd.to_numeric(df["MCV (MW)"], errors="coerce")
    df[f"{prefix}_scheduled_vol_mw"] = pd.to_numeric(df["Final Scheduled Volume (MW)"], errors="coerce")
    
    # MCP (Rs/MWh)
    mcp_col = [c for c in df.columns if "MCP" in c and "Weighted" not in c][0]
    df[f"{prefix}_mcp"] = pd.to_numeric(df[mcp_col], errors="coerce").clip(CERC_PRICE_FLOOR, CERC_PRICE_CAP)

    keep_cols = [
        "date", "block_no", "hour", "session_id", "time_block",
        f"{prefix}_purchase_bid_mw", f"{prefix}_sell_bid_mw",
        f"{prefix}_mcv_mw", f"{prefix}_scheduled_vol_mw", f"{prefix}_mcp"
    ]
    df = df[keep_cols].sort_values(["date", "block_no"]).reset_index(drop=True)
    logger.info("Loaded %s snapshot: %d blocks from %s to %s", market_type.upper(), len(df), df['date'].min(), df['date'].max())
    return df


def load_dam_historical_xlsx(
    path: Union[str, Path],
) -> pd.DataFrame:
    """
    Loads multi-year IEX Day-Ahead Market historical data (DAM.xlsx).
    Handles 233,760 blocks spanning 2018-2024.

    Returns
    -------
    pd.DataFrame
        Standardized historical DAM DataFrame.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"DAM historical file not found: {path}")

    logger.info("Loading historical DAM dataset from %s (230k+ rows)...", path)
    df = pd.read_excel(path)

    # Parse TimeStamp
    ts = pd.to_datetime(df["TimeStamp"])
    df["date"] = ts.dt.date
    df["hour"] = ts.dt.hour + 1
    minute = ts.dt.minute
    df["block_no"] = (ts.dt.hour * 4) + (minute // 15) + 1
    df["session_id"] = ((df["block_no"] - 1) // 2) + 1

    # Standardize column names
    df["dam_purchase_bid_mw"] = pd.to_numeric(df["Purchase Bid (MW)"], errors="coerce")
    df["dam_sell_bid_mw"] = pd.to_numeric(df["Sell Bid (MW)"], errors="coerce")
    df["dam_mcv_mw"] = pd.to_numeric(df["MCV (MW)"], errors="coerce")
    df["dam_scheduled_vol_mw"] = pd.to_numeric(df["Final Scheduled Volume (MW)"], errors="coerce")

    mcp_col = [c for c in df.columns if "MCP" in c and "Weighted" not in c][0]
    df["dam_mcp"] = pd.to_numeric(df[mcp_col], errors="coerce").clip(CERC_PRICE_FLOOR, CERC_PRICE_CAP)

    if "Weighted MCP (Rs/MWh)" in df.columns:
        df["dam_weighted_mcp"] = pd.to_numeric(df["Weighted MCP (Rs/MWh)"], errors="coerce")

    cols = [
        "date", "block_no", "hour", "session_id", "TimeStamp",
        "dam_purchase_bid_mw", "dam_sell_bid_mw", "dam_mcv_mw",
        "dam_scheduled_vol_mw", "dam_mcp"
    ]
    if "dam_weighted_mcp" in df.columns:
        cols.append("dam_weighted_mcp")

    df = df[cols].sort_values(["date", "block_no"]).reset_index(drop=True)
    logger.info("Loaded historical DAM: %d blocks from %s to %s", len(df), df['date'].min(), df['date'].max())
    return df


def load_scada_renewables_timeseries(
    folder_path: Union[str, Path],
    max_files: Optional[int] = None,
) -> pd.DataFrame:
    """
    Parses Grid-India SCADA telemetry files from 'Electricity Demand, Solar and Wind Generation Data/'.
    Extracts 5-minute SCADA measurements and resamples them to 15-minute settlement blocks.

    Extracted features:
    - grid_demand_mw (NLDC_DEMAND)
    - solar_generation_mw (ALL_IND_SOLAR)
    - wind_generation_mw (ALL_INDIA_WIND)
    - thermal_generation_mw (TOTAL_THM_ONLY)
    - hydro_generation_mw (TOTAL_NLDC_HYD)
    - net_demand_mw = demand - (solar + wind)
    """
    folder = Path(folder_path)
    if not folder.exists():
        raise FileNotFoundError(f"SCADA folder not found: {folder}")

    files = sorted(glob.glob(str(folder / "*.xlsx")))
    if max_files:
        files = files[:max_files]

    logger.info("Processing %d SCADA monthly generation files...", len(files))
    all_frames = []

    for fpath in files:
        fname = os.path.basename(fpath)
        try:
            # Sheet1 contains the 5-min SCADA series
            raw = pd.read_excel(fpath, sheet_name="Sheet1")
            if len(raw) < 2:
                continue

            # Row 0 has descriptions: TOTAL_THM_ONLY|P, ALL_IND_SOLAR|P, NLDC_DEMAND|P, etc.
            desc_map = raw.iloc[0].dropna().to_dict()
            tag_to_col = {}
            for col_k, desc_v in desc_map.items():
                tag_name = str(desc_v).split("|")[0].strip()
                tag_to_col[tag_name] = col_k

            # Data starts at row 1
            df_m = raw.iloc[1:].copy()
            time_col = df_m.columns[0]
            df_m["timestamp"] = pd.to_datetime(df_m[time_col], errors="coerce")
            df_m = df_m[df_m["timestamp"].notna()].copy()

            # Extract metrics
            col_demand = tag_to_col.get("NLDC_DEMAND")
            col_solar = tag_to_col.get("ALL_IND_SOLAR")
            col_wind = tag_to_col.get("ALL_INDIA_WIND")
            col_thm = tag_to_col.get("TOTAL_THM_ONLY")
            col_hyd = tag_to_col.get("TOTAL_NLDC_HYD")

            clean_df = pd.DataFrame({"timestamp": df_m["timestamp"]})
            clean_df["grid_demand_mw"] = pd.to_numeric(df_m[col_demand], errors="coerce") if col_demand else np.nan
            clean_df["solar_generation_mw"] = pd.to_numeric(df_m[col_solar], errors="coerce") if col_solar else 0.0
            clean_df["wind_generation_mw"] = pd.to_numeric(df_m[col_wind], errors="coerce") if col_wind else 0.0
            clean_df["thermal_generation_mw"] = pd.to_numeric(df_m[col_thm], errors="coerce") if col_thm else np.nan
            clean_df["hydro_generation_mw"] = pd.to_numeric(df_m[col_hyd], errors="coerce") if col_hyd else np.nan

            # Resample 5-minute telemetry to 15-minute settlement intervals (mean)
            clean_df.set_index("timestamp", inplace=True)
            resampled = clean_df.resample("15min").mean().dropna(subset=["grid_demand_mw"])
            all_frames.append(resampled)
        except Exception as e:
            logger.warning("Could not process %s: %s", fname, e)

    if not all_frames:
        logger.warning("No SCADA frames parsed.")
        return pd.DataFrame()

    full_scada = pd.concat(all_frames).sort_index()
    # Compute net demand and ramp
    full_scada["net_demand_mw"] = full_scada["grid_demand_mw"] - (full_scada["solar_generation_mw"].fillna(0) + full_scada["wind_generation_mw"].fillna(0))
    full_scada["net_demand_ramp_15min"] = full_scada["net_demand_mw"].diff().fillna(0.0)

    # Date and block_no mapping
    ts = full_scada.index
    full_scada["date"] = ts.date
    full_scada["block_no"] = (ts.hour * 4) + (ts.minute // 15) + 1
    full_scada["hour"] = ts.hour + 1

    full_scada.reset_index(inplace=True)
    logger.info("Assembled %d fifteen-minute SCADA intervals from %s to %s", len(full_scada), full_scada['date'].min(), full_scada['date'].max())
    return full_scada


def merge_real_dam_rtm_snapshots(
    dam_path: Union[str, Path],
    rtm_path: Union[str, Path],
) -> pd.DataFrame:
    """
    Merges real DAM and RTM Market Snapshot files into a unified dataset.
    """
    dam = load_market_snapshot(dam_path, market_type="dam")
    rtm = load_market_snapshot(rtm_path, market_type="rtm")

    merged = pd.merge(
        dam,
        rtm,
        on=["date", "block_no", "hour", "session_id", "time_block"],
        how="inner",
    )

    # Cross market spread and tightness
    merged["dam_imbalance_ratio"] = merged["dam_purchase_bid_mw"] / np.maximum(merged["dam_sell_bid_mw"], 1.0)
    merged["rtm_imbalance_ratio"] = merged["rtm_purchase_bid_mw"] / np.maximum(merged["rtm_sell_bid_mw"], 1.0)
    merged["dam_rtm_spread"] = merged["rtm_mcp"] - merged["dam_mcp"]

    # Target: RTM high price spike (top 10% or >= P90)
    p90 = merged["rtm_mcp"].quantile(0.90)
    merged["rtm_spike"] = (merged["rtm_mcp"] >= p90).astype(int)

    logger.info("Merged real DAM-RTM snapshots: %d blocks (RTM P90 = Rs %.1f/MWh)", len(merged), p90)
    return merged
