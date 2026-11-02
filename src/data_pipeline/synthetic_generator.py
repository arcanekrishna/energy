"""
Calibrated Synthetic Generator for Indian Electricity Market Data.

Generates structurally realistic IEX DAM and RTM datasets incorporating:
- 96 blocks per day (15-min intervals)
- Diurnal solar duck curve & evening ramp stress (Blocks 68-82)
- Indian seasonal variations (Summer heatwave, Monsoon dip, Post-monsoon, Winter)
- CERC statutory price bounds: Rs 0 - Rs 10,000 / MWh (Rs 0 - Rs 10 / kWh)
- Realistic cross-market tightness propagation: P(RTM stress) increases with DAM purchase/sell ratio
- Exact schema compatibility with real IEX exports
"""

from __future__ import annotations

import datetime as dt
from typing import Optional, Union

import numpy as np
import pandas as pd

try:
    from src.data_pipeline.iex_schema import (
        BLOCKS_PER_DAY,
        CERC_PRICE_CAP,
        CERC_PRICE_FLOOR,
        SESSIONS_PER_DAY,
        block_to_time,
    )
except ImportError:
    try:
        from indian_power_market.src.data_pipeline.iex_schema import (
            BLOCKS_PER_DAY,
            CERC_PRICE_CAP,
            CERC_PRICE_FLOOR,
            SESSIONS_PER_DAY,
            block_to_time,
        )
    except ImportError:
        from .iex_schema import (
            BLOCKS_PER_DAY,
            CERC_PRICE_CAP,
            CERC_PRICE_FLOOR,
            SESSIONS_PER_DAY,
            block_to_time,
        )


def generate_synthetic_rtm(
    dam_df: pd.DataFrame,
    seed: int = 42,
    stress_coupling_strength: float = 3.5,
) -> pd.DataFrame:
    """
    Generates a synthetic Real-Time Market (RTM) dataset temporally aligned
    with an existing Day-Ahead Market (DAM) DataFrame.

    The generator embeds a formal logistic coupling between Day-Ahead market
    tightness and Real-Time price spikes, enabling empirical hypothesis testing.

    Parameters
    ----------
    dam_df : pd.DataFrame
        DataFrame containing at least 'date', 'block_no', and 'dam_mcp'
        (optionally 'dam_purchase_bid_mw', 'dam_sell_bid_mw').
    seed : int, default=42
        Random seed for reproducibility.
    stress_coupling_strength : float, default=3.5
        Logistic slope controlling how strongly high DAM purchase/sell ratio
        increases RTM stress probability.

    Returns
    -------
    pd.DataFrame
        Synthetic RTM DataFrame matching canonical schema.
    """
    np.random.seed(seed)
    df = dam_df.copy()
    n = len(df)

    if n == 0:
        raise ValueError("Input DAM DataFrame is empty.")

    # Canonicalize required columns
    blocks = df["block_no"].values if "block_no" in df.columns else np.tile(np.arange(1, 97), int(np.ceil(n / 96)))[:n]
    hours = ((blocks - 1) // 4) + 1
    session_ids = ((blocks - 1) // 2) + 1

    # Price column resolution
    price_col = "dam_mcp" if "dam_mcp" in df.columns else ("dam_mcp_rs_mwh" if "dam_mcp_rs_mwh" in df.columns else None)
    if price_col is None:
        raise ValueError("DAM DataFrame must contain 'dam_mcp' or 'dam_mcp_rs_mwh'.")
    dam_prices = df[price_col].values.astype(float)

    # DAM market tightness ratio
    if "dam_purchase_bid_mw" in df.columns and "dam_sell_bid_mw" in df.columns:
        dam_ratio = df["dam_purchase_bid_mw"].values / np.maximum(df["dam_sell_bid_mw"].values, 1.0)
    else:
        # Proxy from price percentile rank
        pct = pd.Series(dam_prices).rank(pct=True).values
        dam_ratio = 0.70 + 0.60 * pct

    # Logistic stress probability: P(stress) = sigmoid(beta * (ratio - threshold))
    stress_prob = 1.0 / (1.0 + np.exp(-stress_coupling_strength * (dam_ratio - 1.12)))

    # Regime-specific modulations
    # Evening solar ramp (blocks 68-82, 17:00 - 20:30 IST)
    evening_mask = (blocks >= 68) & (blocks <= 82)
    stress_prob[evening_mask] = np.clip(stress_prob[evening_mask] * 1.60, 0.0, 0.95)

    # Morning ramp (blocks 28-36)
    morning_mask = (blocks >= 28) & (blocks <= 36)
    stress_prob[morning_mask] = np.clip(stress_prob[morning_mask] * 1.15, 0.0, 0.85)

    # Night off-peak (blocks 1-16)
    night_mask = blocks <= 16
    stress_prob[night_mask] = stress_prob[night_mask] * 0.50

    # Stochastic shock indicator
    shock_active = (np.random.uniform(0.0, 1.0, n) < stress_prob).astype(float)

    # Bids generation
    if "dam_purchase_bid_mw" in df.columns and "dam_sell_bid_mw" in df.columns:
        base_rtm_purchase = df["dam_purchase_bid_mw"].values * np.random.uniform(0.20, 0.35, n)
        base_rtm_sell = df["dam_sell_bid_mw"].values * np.random.uniform(0.18, 0.32, n)
    else:
        base_rtm_purchase = 2200.0 + 900.0 * dam_ratio + np.random.normal(0, 200, n)
        base_rtm_sell = 2600.0 + np.random.normal(0, 300, n)

    # Shocks compress sell bids and surge purchase bids
    rtm_purchase = np.maximum(500.0, base_rtm_purchase + shock_active * np.random.uniform(1500.0, 3500.0, n))
    rtm_sell = np.maximum(400.0, base_rtm_sell - shock_active * np.random.uniform(500.0, 1500.0, n))

    rtm_ratio = rtm_purchase / np.maximum(rtm_sell, 1.0)
    rtm_mcv = np.minimum(rtm_purchase, rtm_sell) * np.random.uniform(0.85, 0.95, n)

    # RTM MCP formulation
    spread_mult = (rtm_ratio / np.maximum(dam_ratio, 0.50)) ** 1.60
    rtm_mcp = dam_prices * spread_mult + shock_active * np.random.uniform(1200.0, 4200.0, n)
    rtm_mcp += np.random.normal(0, 120, n)
    rtm_mcp = np.clip(rtm_mcp, CERC_PRICE_FLOOR + 500.0, CERC_PRICE_CAP)

    dates = df["date"].values if "date" in df.columns else pd.date_range("2024-01-01", periods=n, freq="15min")

    rtm_df = pd.DataFrame({
        "date": dates,
        "block_no": blocks,
        "hour": hours,
        "session_id": session_ids,
        "rtm_purchase_bid_mw": np.round(rtm_purchase, 2),
        "rtm_sell_bid_mw": np.round(rtm_sell, 2),
        "rtm_mcv_mw": np.round(rtm_mcv, 2),
        "rtm_mcp": np.round(rtm_mcp, 2),
        "_rtm_shock_flag": shock_active.astype(int),
    })

    return rtm_df


def generate_full_synthetic(
    start_date: str = "2024-01-01",
    days: int = 365,
    seed: int = 42,
) -> pd.DataFrame:
    """
    Generates a complete, self-contained synthetic benchmark dataset containing
    both DAM and RTM with all 96 blocks, seasonal variations, and diurnal profiles.

    Parameters
    ----------
    start_date : str, default="2024-01-01"
        Starting date in YYYY-MM-DD format.
    days : int, default=365
        Number of days to simulate.
    seed : int, default=42
        Random seed for reproducibility.

    Returns
    -------
    pd.DataFrame
        Complete aligned dataset containing DAM and RTM columns.
    """
    np.random.seed(seed)
    total_blocks = days * BLOCKS_PER_DAY

    dates_idx = pd.date_range(start=start_date, periods=days, freq="D")
    repeated_dates = np.repeat(dates_idx, BLOCKS_PER_DAY)
    block_nums = np.tile(np.arange(1, BLOCKS_PER_DAY + 1), days)
    hours = ((block_nums - 1) // 4) + 1
    session_ids = ((block_nums - 1) // 2) + 1

    # Seasonal pattern
    doy = repeated_dates.dayofyear.values
    is_weekend = (repeated_dates.dayofweek.values >= 5).astype(float)
    seasonality = (
        1.0
        + 0.18 * np.sin(2 * np.pi * (doy - 80) / 365.0)  # Summer heatwave
        - 0.08 * ((doy >= 180) & (doy <= 230)).astype(float)  # Monsoon dip
    )

    # Diurnal duck curve pattern
    b = block_nums
    diurnal = (
        1.0
        + 0.22 * np.exp(-((b - 32) ** 2) / 35.0)  # Morning industrial peak
        - 0.28 * np.exp(-((b - 50) ** 2) / 60.0)  # Midday solar valley
        + 0.48 * np.exp(-((b - 75) ** 2) / 45.0)  # Evening solar drop ramp
        - 0.18 * np.exp(-((b - 12) ** 2) / 40.0)  # Night baseload
        - 0.06 * is_weekend
    )

    base_demand_mw = 7500.0 * seasonality * diurnal

    # DAM quantities
    dam_purchase = np.maximum(2500.0, base_demand_mw * np.random.normal(1.0, 0.05, total_blocks) * 1.15)
    solar_supply = np.maximum(0.0, 3200.0 * np.sin(np.pi * np.clip(b - 36, 0, 36) / 36.0))
    dam_sell = np.maximum(3000.0, 8200.0 * seasonality + solar_supply + np.random.normal(0, 300, total_blocks))

    dam_ratio = dam_purchase / np.maximum(dam_sell, 1.0)
    dam_mcv = np.minimum(dam_purchase, dam_sell) * np.random.uniform(0.88, 0.96, total_blocks)

    base_price = 3600.0 * seasonality
    dam_mcp = base_price * (dam_ratio ** 1.8) + np.random.normal(0, 150, total_blocks)
    dam_mcp = np.clip(dam_mcp, 500.0, CERC_PRICE_CAP)

    dam_df = pd.DataFrame({
        "date": repeated_dates,
        "block_no": block_nums,
        "hour": hours,
        "session_id": session_ids,
        "dam_purchase_bid_mw": np.round(dam_purchase, 2),
        "dam_sell_bid_mw": np.round(dam_sell, 2),
        "dam_mcv_mw": np.round(dam_mcv, 2),
        "dam_mcp": np.round(dam_mcp, 2),
    })

    # Generate RTM coupled to this DAM
    rtm_df = generate_synthetic_rtm(dam_df, seed=seed)

    merged = pd.merge(dam_df, rtm_df, on=["date", "block_no", "hour", "session_id"])
    return merged
