"""
Multi-horizon forecast alignment for DAM→RTM stress propagation.

Provides pre-defined forecast horizons (1h, 2h, 4h, day-ahead), dataset
preparation with correct temporal lagging to prevent look-ahead bias,
and strict chronological train/test splitting.

Indian Electricity Market Context
----------------------------------
- 96 fifteen-minute time blocks per day.
- DAM clears on Day D-1 at ~14:00 IST for all 96 blocks of Day D.
- RTM has 48 sessions, each clearing 2 blocks; gate closes 1h before delivery.
- Zero look-ahead bias: features at time T must only use data available before T.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import List, Optional, Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Forecast horizon definition
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ForecastHorizon:
    """Immutable specification of a forecast lead time.

    Attributes
    ----------
    name : str
        Human-readable identifier, e.g. ``"1h_ahead"``.
    lead_blocks : int
        Number of 15-minute blocks in the lead time.
    lead_hours : float
        Lead time expressed in hours (``lead_blocks * 0.25``).
    """

    name: str
    lead_blocks: int
    lead_hours: float

    def __post_init__(self) -> None:
        if self.lead_blocks < 1:
            raise ValueError(f"lead_blocks must be >= 1, got {self.lead_blocks}")
        if self.lead_hours <= 0:
            raise ValueError(f"lead_hours must be > 0, got {self.lead_hours}")


# Pre-defined horizons -------------------------------------------------------

HORIZON_1H: ForecastHorizon = ForecastHorizon("1h_ahead", 4, 1.0)
"""1-hour-ahead horizon (4 × 15-min blocks)."""

HORIZON_2H: ForecastHorizon = ForecastHorizon("2h_ahead", 8, 2.0)
"""2-hour-ahead horizon (8 × 15-min blocks)."""

HORIZON_4H: ForecastHorizon = ForecastHorizon("4h_ahead", 16, 4.0)
"""4-hour-ahead horizon (16 × 15-min blocks)."""

HORIZON_DAY_AHEAD: ForecastHorizon = ForecastHorizon("day_ahead", 96, 24.0)
"""Day-ahead horizon (96 × 15-min blocks, i.e. full 24 hours)."""

ALL_HORIZONS: List[ForecastHorizon] = [
    HORIZON_1H,
    HORIZON_2H,
    HORIZON_4H,
    HORIZON_DAY_AHEAD,
]
"""All pre-defined horizons for convenient iteration."""

# ---------------------------------------------------------------------------
# Feature columns classification
# ---------------------------------------------------------------------------

# Columns that are inherently targets / labels — never used as features.
_TARGET_COLUMNS = {
    "rtm_price",
    "rtm_mcp",
    "spike",
    "price_spike",
    "rtm_spike",
    "y_spike",
    "y_price",
}

# Columns that carry temporal metadata — kept as-is.
_TEMPORAL_INDEX_COLUMNS = {
    "date",
    "datetime",
    "timestamp",
    "block",
    "block_no",
    "time_block",
}


def _classify_feature_columns(
    columns: pd.Index,
) -> Tuple[List[str], List[str], List[str]]:
    """Split column names into (feature_cols, target_cols, index_cols).

    Parameters
    ----------
    columns : pd.Index
        All columns from the merged market DataFrame.

    Returns
    -------
    feature_cols : list[str]
        Columns eligible to be used as model features.
    target_cols : list[str]
        Columns that represent prediction targets.
    index_cols : list[str]
        Temporal / index columns.
    """
    feature_cols: List[str] = []
    target_cols: List[str] = []
    index_cols: List[str] = []

    for col in columns:
        col_lower = col.lower()
        if col_lower in _TARGET_COLUMNS:
            target_cols.append(col)
        elif col_lower in _TEMPORAL_INDEX_COLUMNS:
            index_cols.append(col)
        else:
            feature_cols.append(col)

    return feature_cols, target_cols, index_cols


# ---------------------------------------------------------------------------
# Dataset preparation with look-ahead-safe lagging
# ---------------------------------------------------------------------------


def prepare_horizon_dataset(
    df: pd.DataFrame,
    horizon: ForecastHorizon,
    target_price_col: str = "rtm_price",
    target_spike_col: str = "spike",
) -> Tuple[pd.DataFrame, pd.Series, pd.Series, List[str]]:
    """Prepare a look-ahead-safe dataset for a given forecast horizon.

    For a horizon of *h* blocks, every feature row at index *t* is shifted
    backward by *h* blocks so that features available at time ``t - h`` are
    aligned with the target at time *t*.  This guarantees zero look-ahead bias.

    Parameters
    ----------
    df : pd.DataFrame
        Merged market DataFrame containing DAM, RTM, and derived features.
        Must be sorted chronologically (ascending).
    horizon : ForecastHorizon
        The forecast horizon specification.
    target_price_col : str, default ``"rtm_price"``
        Column name for the continuous price target.
    target_spike_col : str, default ``"spike"``
        Column name for the binary spike target.

    Returns
    -------
    X : pd.DataFrame
        Feature matrix with lagged features (NaN warm-up rows dropped).
    y_spike : pd.Series
        Binary spike labels aligned with ``X``.
    y_price : pd.Series
        Continuous price targets aligned with ``X``.
    feature_names : list[str]
        Ordered list of feature column names in ``X``.

    Raises
    ------
    ValueError
        If required target columns are missing from *df*.
    """
    df = df.copy()

    # --- Validate targets exist ---
    missing = []
    if target_price_col not in df.columns:
        missing.append(target_price_col)
    if target_spike_col not in df.columns:
        missing.append(target_spike_col)
    if missing:
        raise ValueError(
            f"Target columns missing from DataFrame: {missing}. "
            f"Available columns: {list(df.columns)}"
        )

    # --- Classify columns ---
    feature_cols, _target_cols, _index_cols = _classify_feature_columns(df.columns)

    if not feature_cols:
        raise ValueError(
            "No feature columns found after excluding targets and index columns."
        )

    logger.info(
        "Horizon '%s': %d feature cols, lead=%d blocks (%.1fh)",
        horizon.name,
        len(feature_cols),
        horizon.lead_blocks,
        horizon.lead_hours,
    )

    # --- Extract targets (unshifted — they stay at their natural time) ---
    y_price_full = df[target_price_col].copy()
    y_spike_full = df[target_spike_col].astype(np.int8).copy()

    # --- Lag features by horizon.lead_blocks ---
    # shift(+h) moves features *forward* so that the feature row originally at
    # time t now sits at row t+h.  The target at row t+h is therefore predicted
    # using information from time t (i.e., h blocks in the past).
    X_full = df[feature_cols].shift(horizon.lead_blocks)

    # --- Drop warm-up NaN rows ---
    valid_mask = X_full.notna().all(axis=1)
    X = X_full.loc[valid_mask].reset_index(drop=True)
    y_spike = y_spike_full.loc[valid_mask].reset_index(drop=True)
    y_price = y_price_full.loc[valid_mask].reset_index(drop=True)

    feature_names = list(X.columns)

    logger.info(
        "Horizon '%s': %d samples after dropping %d warm-up rows.",
        horizon.name,
        len(X),
        int((~valid_mask).sum()),
    )

    return X, y_spike, y_price, feature_names


# ---------------------------------------------------------------------------
# Chronological train / test split
# ---------------------------------------------------------------------------


def temporal_train_test_split(
    df: pd.DataFrame,
    train_frac: float = 0.7,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Split a DataFrame chronologically — no shuffling.

    The first ``train_frac`` fraction of rows becomes the training set and the
    remainder becomes the test set.  This preserves temporal order, which is
    essential for any time-series forecasting task where shuffling would leak
    future information into training.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame sorted in chronological order.
    train_frac : float, default 0.7
        Fraction of rows allocated to the training set.  Must be in (0, 1).

    Returns
    -------
    df_train : pd.DataFrame
        Training portion (first ``train_frac`` rows).
    df_test : pd.DataFrame
        Test portion (remaining rows).

    Raises
    ------
    ValueError
        If *train_frac* is not in (0, 1) or *df* is empty.
    """
    if not 0.0 < train_frac < 1.0:
        raise ValueError(f"train_frac must be in (0, 1), got {train_frac}")
    if df.empty:
        raise ValueError("Cannot split an empty DataFrame.")

    split_idx = int(len(df) * train_frac)

    # Guarantee at least 1 row in each split.
    split_idx = max(1, min(split_idx, len(df) - 1))

    df_train = df.iloc[:split_idx].reset_index(drop=True)
    df_test = df.iloc[split_idx:].reset_index(drop=True)

    logger.info(
        "Temporal split: %d train rows (%.1f%%), %d test rows (%.1f%%)",
        len(df_train),
        100.0 * len(df_train) / len(df),
        len(df_test),
        100.0 * len(df_test) / len(df),
    )

    return df_train, df_test
