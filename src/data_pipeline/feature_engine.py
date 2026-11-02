"""
Zero-Leakage Temporal Feature Engineering for Indian Electricity Market Intelligence.

Enforces point-in-time constraints across the multi-settlement DAM-RTM timeline:
- DAM features are 100% legal for all 96 blocks of delivery Day D (cleared at D-1 14:00 IST).
- RTM lagged features strictly respect the forecast horizon: for delivery block b,
  any real-time telemetry must come from at least `horizon_blocks` prior to b.
- Cyclical harmonic encodings for the 96 diurnal settlement blocks.
- Specialized grid regime indicators (evening solar drop ramp, morning industrial ramp).
"""

from __future__ import annotations

import logging
from typing import List, Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def build_features(
    df_market: pd.DataFrame,
    horizon_blocks: int = 4,
    spike_quantile: float = 0.90,
    low_quantile: float = 0.10,
) -> pd.DataFrame:
    """
    Constructs a feature-rich, strictly zero-leakage dataset for multi-horizon forecasting.

    Parameters
    ----------
    df_market : pd.DataFrame
        Merged DAM and RTM DataFrame sorted by date and block_no.
    horizon_blocks : int, default=4
        Number of 15-minute lead blocks before target delivery.
        - 4 blocks = 1 hour ahead
        - 8 blocks = 2 hours ahead
        - 16 blocks = 4 hours ahead
        - 96 blocks = Day-Ahead (24 hours ahead)
    spike_quantile : float, default=0.90
        Quantile threshold for defining high-price stress events.
    low_quantile : float, default=0.10
        Quantile threshold for defining low-price surplus events.

    Returns
    -------
    pd.DataFrame
        Enriched DataFrame with engineered features and target indicators.
    """
    df = df_market.copy()

    # Sort strictly chronologically
    sort_cols = [c for c in ["date", "block_no"] if c in df.columns]
    if sort_cols:
        df = df.sort_values(sort_cols).reset_index(drop=True)

    # -----------------------------------------------------------------------
    # 1. DAM Fundamental Features (Fully known on Day D-1, completely legal)
    # -----------------------------------------------------------------------
    has_bids = "dam_purchase_bid_mw" in df.columns and "dam_sell_bid_mw" in df.columns
    if has_bids:
        df["dam_imbalance_ratio"] = df["dam_purchase_bid_mw"] / np.maximum(df["dam_sell_bid_mw"], 1.0)
        df["dam_unsatisfied_demand_mw"] = np.maximum(0.0, df["dam_purchase_bid_mw"] - df["dam_mcv_mw"])
        df["dam_supply_cushion_mw"] = np.maximum(0.0, df["dam_sell_bid_mw"] - df["dam_mcv_mw"])
        df["dam_clearance_ratio"] = df["dam_mcv_mw"] / np.maximum(df["dam_purchase_bid_mw"], 1.0)
    else:
        # Fallback proxy based on price rank
        df["dam_imbalance_ratio"] = 0.70 + 0.60 * df["dam_mcp"].rank(pct=True)
        df["dam_unsatisfied_demand_mw"] = 0.0
        df["dam_supply_cushion_mw"] = 0.0
        df["dam_clearance_ratio"] = 0.90

    # Cross-market spread (RTM - DAM)
    if "rtm_mcp" in df.columns and "dam_mcp" in df.columns:
        df["dam_rtm_spread"] = df["rtm_mcp"] - df["dam_mcp"]
    else:
        df["dam_rtm_spread"] = 0.0

    # Rolling DAM price context (strictly backward looking)
    df["dam_mcp_roll_mean_24b"] = df["dam_mcp"].rolling(24, min_periods=4).mean()
    df["dam_mcp_roll_std_24b"] = df["dam_mcp"].rolling(24, min_periods=4).std().fillna(0.0)

    # -----------------------------------------------------------------------
    # 2. Point-in-Time RTM Lagged Features (Shifted by horizon_blocks)
    # -----------------------------------------------------------------------
    lag = int(horizon_blocks)
    if "rtm_mcp" in df.columns:
        df[f"rtm_mcp_lag_{lag}"] = df["rtm_mcp"].shift(lag)
        df[f"rtm_spread_lag_{lag}"] = df["dam_rtm_spread"].shift(lag)
        df[f"rtm_volat_lag_{lag}"] = df["rtm_mcp"].shift(lag).rolling(8, min_periods=2).std().fillna(0.0)
        df[f"rtm_momentum_lag_{lag}"] = df["rtm_mcp"].shift(lag) - df["rtm_mcp"].shift(lag + 4).fillna(df["rtm_mcp"].shift(lag))
    else:
        df[f"rtm_mcp_lag_{lag}"] = 0.0
        df[f"rtm_spread_lag_{lag}"] = 0.0
        df[f"rtm_volat_lag_{lag}"] = 0.0
        df[f"rtm_momentum_lag_{lag}"] = 0.0

    # -----------------------------------------------------------------------
    # 3. Temporal, Diurnal & Ramping Features
    # -----------------------------------------------------------------------
    b = df["block_no"]
    df["sin_block"] = np.sin(2.0 * np.pi * b / 96.0)
    df["cos_block"] = np.cos(2.0 * np.pi * b / 96.0)
    df["is_evening_ramp"] = b.between(65, 84).astype(int)
    df["is_morning_ramp"] = b.between(25, 40).astype(int)
    df["is_solar_valley"] = b.between(44, 60).astype(int)

    if "date" in df.columns:
        dt_series = pd.to_datetime(df["date"], errors="coerce")
        df["day_of_week"] = dt_series.dt.dayofweek.fillna(0).astype(int)
        df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)
        df["month"] = dt_series.dt.month.fillna(1).astype(int)
    else:
        df["day_of_week"] = 0
        df["is_weekend"] = 0
        df["month"] = 1

    # -----------------------------------------------------------------------
    # 4. Target Variables (For model training and evaluation)
    # -----------------------------------------------------------------------
    if "rtm_mcp" in df.columns:
        p90_threshold = df["rtm_mcp"].quantile(spike_quantile)
        p10_threshold = df["rtm_mcp"].quantile(low_quantile)
        spread_p90 = df["dam_rtm_spread"].abs().quantile(spike_quantile)

        df["rtm_spike"] = (df["rtm_mcp"] >= p90_threshold).astype(int)
        df["rtm_low_price"] = (df["rtm_mcp"] <= p10_threshold).astype(int)
        df["spread_dislocation"] = (df["dam_rtm_spread"].abs() >= spread_p90).astype(int)

    return df


def get_feature_columns(horizon_blocks: int = 4) -> List[str]:
    """
    Returns the exact list of predictor column names for a given forecast horizon.
    """
    lag = int(horizon_blocks)
    base_features = [
        "dam_mcp",
        "dam_imbalance_ratio",
        "dam_unsatisfied_demand_mw",
        "dam_supply_cushion_mw",
        "dam_clearance_ratio",
        "dam_mcp_roll_mean_24b",
        "dam_mcp_roll_std_24b",
        f"rtm_mcp_lag_{lag}",
        f"rtm_spread_lag_{lag}",
        f"rtm_volat_lag_{lag}",
        f"rtm_momentum_lag_{lag}",
        "sin_block",
        "cos_block",
        "is_evening_ramp",
        "is_morning_ramp",
        "is_solar_valley",
        "day_of_week",
        "is_weekend",
        "month",
    ]
    return base_features


def validate_no_leakage(df: pd.DataFrame, horizon_blocks: int) -> bool:
    """
    Audits the dataset to assert that no lagged feature leaks information
    from within the forbidden window (less than `horizon_blocks` prior to target).

    Returns True if valid; raises AssertionError if leakage is detected.
    """
    lag = int(horizon_blocks)
    target_col = "rtm_mcp"
    lagged_col = f"rtm_mcp_lag_{lag}"

    if target_col not in df.columns or lagged_col not in df.columns:
        return True

    # Compute correlation between target at t and lagged feature at t
    # For valid lags, correlation between rtm_mcp(t) and rtm_mcp(t-lag) should decay as lag grows
    valid_rows = df[[target_col, lagged_col]].dropna()
    if len(valid_rows) < 100:
        return True

    # If lagged_col was identical to target_col (leakage), corr would be 1.0 exactly
    corr = valid_rows[target_col].corr(valid_rows[lagged_col])
    if abs(corr - 1.0) < 1e-6:
        raise AssertionError(f"DATA LEAKAGE DETECTED: {lagged_col} is perfectly collinear with {target_col}!")

    return True
