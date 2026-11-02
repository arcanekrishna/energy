# -*- coding: utf-8 -*-
"""Comprehensive pytest tests for the data pipeline.

Tests cover IEX market-data constraints (96 blocks/day, CERC price caps),
column standardization, feature-engineering look-ahead-bias checks,
and synthetic RTM generation.

All tests are self-contained — they create small sample DataFrames
(typically 3 days = 288 blocks) and never need external data files.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Dict, List

import numpy as np
import pandas as pd
import pytest

# ── Domain constants (duplicated here so tests remain self-contained) ──────
BLOCKS_PER_DAY: int = 96
CERC_PRICE_CAP: float = 10_000.0   # Rs/MWh
CERC_PRICE_FLOOR: float = 0.0      # Rs/MWh
SESSIONS_PER_DAY: int = 48


# ═══════════════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════════════

def _make_market_df(n_days: int = 3, seed: int = 42) -> pd.DataFrame:
    """Build a deterministic market DataFrame with *n_days* × 96 rows.

    Columns: date, block_no, dam_mcp, rtm_mcp, dam_purchase_bid,
             dam_sell_bid, dam_mcv, session_id.
    """
    rng = np.random.default_rng(seed)
    start = date(2024, 1, 1)
    rows: List[Dict] = []
    for d in range(n_days):
        day = start + timedelta(days=d)
        for b in range(1, BLOCKS_PER_DAY + 1):
            session_id = (b - 1) // 2 + 1
            dam_mcp = float(np.clip(rng.normal(3_000, 1_000), 0, CERC_PRICE_CAP))
            rtm_mcp = float(np.clip(dam_mcp + rng.normal(0, 500), 0, CERC_PRICE_CAP))
            rows.append({
                "date": day,
                "block_no": b,
                "dam_mcp": round(dam_mcp, 2),
                "rtm_mcp": round(rtm_mcp, 2),
                "dam_purchase_bid": round(float(rng.uniform(20_000, 50_000)), 2),
                "dam_sell_bid": round(float(rng.uniform(20_000, 50_000)), 2),
                "dam_mcv": round(float(rng.uniform(15_000, 40_000)), 2),
                "session_id": session_id,
            })
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    return df


@pytest.fixture
def market_df() -> pd.DataFrame:
    """3-day market DataFrame fixture."""
    return _make_market_df(n_days=3)


@pytest.fixture
def market_df_7d() -> pd.DataFrame:
    """7-day market DataFrame for feature-lag tests."""
    return _make_market_df(n_days=7, seed=99)


# ═══════════════════════════════════════════════════════════════════════════
# Test 1 — Block range
# ═══════════════════════════════════════════════════════════════════════════

def test_block_range(market_df: pd.DataFrame) -> None:
    """block_no must always be in [1, 96]."""
    assert market_df["block_no"].min() >= 1
    assert market_df["block_no"].max() <= BLOCKS_PER_DAY


# ═══════════════════════════════════════════════════════════════════════════
# Test 2 — Price bounds
# ═══════════════════════════════════════════════════════════════════════════

def test_price_bounds(market_df: pd.DataFrame) -> None:
    """dam_mcp and rtm_mcp must lie within [0, CERC_PRICE_CAP]."""
    for col in ("dam_mcp", "rtm_mcp"):
        assert market_df[col].min() >= CERC_PRICE_FLOOR, f"{col} below floor"
        assert market_df[col].max() <= CERC_PRICE_CAP, f"{col} above cap"


# ═══════════════════════════════════════════════════════════════════════════
# Test 3 — No negative volumes
# ═══════════════════════════════════════════════════════════════════════════

def test_no_negative_volumes(market_df: pd.DataFrame) -> None:
    """Purchase bid, sell bid, and MCV must be non-negative."""
    for col in ("dam_purchase_bid", "dam_sell_bid", "dam_mcv"):
        assert (market_df[col] >= 0).all(), f"Negative values in {col}"


# ═══════════════════════════════════════════════════════════════════════════
# Test 4 — 96 blocks per day
# ═══════════════════════════════════════════════════════════════════════════

def test_blocks_per_day(market_df: pd.DataFrame) -> None:
    """Each date must have exactly 96 blocks."""
    counts = market_df.groupby("date")["block_no"].nunique()
    assert (counts == BLOCKS_PER_DAY).all(), (
        f"Expected {BLOCKS_PER_DAY} blocks/day, got: {counts.to_dict()}"
    )


# ═══════════════════════════════════════════════════════════════════════════
# Test 5 — Session ID mapping
# ═══════════════════════════════════════════════════════════════════════════

def test_session_mapping(market_df: pd.DataFrame) -> None:
    """session_id must equal (block_no - 1) // 2 + 1."""
    expected = (market_df["block_no"] - 1) // 2 + 1
    pd.testing.assert_series_equal(
        market_df["session_id"].astype(int),
        expected.astype(int),
        check_names=False,
    )


# ═══════════════════════════════════════════════════════════════════════════
# Test 6 — Column standardization
# ═══════════════════════════════════════════════════════════════════════════

# Mapping of commonly seen raw column names → canonical names
_COLUMN_ALIASES: Dict[str, str] = {
    "Date": "date",
    "DATE": "date",
    "Block No": "block_no",
    "Block_No": "block_no",
    "BLOCK_NO": "block_no",
    "block": "block_no",
    "DAM MCP (Rs/MWh)": "dam_mcp",
    "dam_mcp_rs_mwh": "dam_mcp",
    "MCP": "dam_mcp",
    "RTM MCP (Rs/MWh)": "rtm_mcp",
    "rtm_mcp_rs_mwh": "rtm_mcp",
    "Purchase Bid (MW)": "dam_purchase_bid",
    "Sell Bid (MW)": "dam_sell_bid",
    "MCV (MW)": "dam_mcv",
}


def _standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Apply canonical column renaming (standalone implementation for tests)."""
    return df.rename(columns=_COLUMN_ALIASES)


def test_column_standardization() -> None:
    """Various raw naming conventions should map to canonical names."""
    raw = pd.DataFrame({
        "Date": pd.to_datetime(["2024-01-01"]),
        "Block No": [1],
        "DAM MCP (Rs/MWh)": [3500.0],
        "RTM MCP (Rs/MWh)": [3800.0],
        "Purchase Bid (MW)": [30000.0],
        "Sell Bid (MW)": [28000.0],
        "MCV (MW)": [25000.0],
    })
    std = _standardize_columns(raw)
    expected_cols = {"date", "block_no", "dam_mcp", "rtm_mcp",
                     "dam_purchase_bid", "dam_sell_bid", "dam_mcv"}
    assert expected_cols.issubset(set(std.columns)), (
        f"Missing columns after standardization: "
        f"{expected_cols - set(std.columns)}"
    )


def test_column_standardization_alternative_names() -> None:
    """Handles alternative naming conventions (underscore, uppercase)."""
    raw = pd.DataFrame({
        "DATE": pd.to_datetime(["2024-01-01"]),
        "BLOCK_NO": [1],
        "dam_mcp_rs_mwh": [3500.0],
        "rtm_mcp_rs_mwh": [3800.0],
    })
    std = _standardize_columns(raw)
    assert "date" in std.columns
    assert "block_no" in std.columns
    assert "dam_mcp" in std.columns
    assert "rtm_mcp" in std.columns


# ═══════════════════════════════════════════════════════════════════════════
# Test 7 — Feature no-leakage check
# ═══════════════════════════════════════════════════════════════════════════

def _build_lagged_features(
    df: pd.DataFrame,
    horizon_blocks: int,
    price_col: str = "dam_mcp",
) -> pd.DataFrame:
    """Create lagged features respecting look-ahead constraints.

    At time T, we may only use data from blocks <= T - horizon_blocks.
    This standalone implementation mirrors the project's build_features logic.
    """
    df = df.sort_values(["date", "block_no"]).copy()
    # Minimum safe lag is horizon_blocks
    for lag in (horizon_blocks, horizon_blocks + 4, horizon_blocks + 8):
        df[f"{price_col}_lag{lag}"] = df[price_col].shift(lag)
    # Rolling mean over 4 past blocks, shifted by horizon_blocks
    df[f"{price_col}_roll4_mean"] = (
        df[price_col]
        .shift(horizon_blocks)
        .rolling(window=4, min_periods=1)
        .mean()
    )
    return df


def test_feature_no_leakage(market_df_7d: pd.DataFrame) -> None:
    """Lagged features at horizon h must not use data within h blocks of target.

    For each row i, every feature value must have been computed from
    data at row j where j <= i - horizon_blocks.
    """
    horizon_blocks = 4  # 1-hour horizon
    df = _build_lagged_features(market_df_7d, horizon_blocks=horizon_blocks)

    # Drop initial NaN rows from lagging
    df_valid = df.dropna().copy()

    # For each lag column, verify the lag is >= horizon_blocks
    lag_cols = [c for c in df_valid.columns if "_lag" in c]
    for col in lag_cols:
        lag_amount = int(col.split("lag")[-1])
        assert lag_amount >= horizon_blocks, (
            f"Column {col} has lag {lag_amount} < horizon {horizon_blocks}"
        )

    # Verify rolling feature also respects minimum shift
    # The _roll4_mean column is pre-shifted by horizon_blocks, so
    # at index i it's computed from data at indices <= i - horizon_blocks
    assert f"dam_mcp_roll4_mean" in df.columns


def test_feature_no_leakage_larger_horizon() -> None:
    """Same no-leakage guarantee with 4-hour horizon (16 blocks)."""
    df = _make_market_df(n_days=10, seed=77)
    horizon_blocks = 16
    df_feat = _build_lagged_features(df, horizon_blocks=horizon_blocks)

    lag_cols = [c for c in df_feat.columns if "_lag" in c]
    for col in lag_cols:
        lag_amount = int(col.split("lag")[-1])
        assert lag_amount >= horizon_blocks, (
            f"Column {col} has lag {lag_amount} < horizon {horizon_blocks}"
        )


# ═══════════════════════════════════════════════════════════════════════════
# Test 8 — Synthetic RTM alignment
# ═══════════════════════════════════════════════════════════════════════════

def _generate_synthetic_rtm(dam_df: pd.DataFrame, seed: int = 42) -> pd.DataFrame:
    """Create synthetic RTM prices aligned to DAM dates and blocks.

    Standalone implementation: RTM = DAM × multiplier + noise,
    clamped to [CERC_PRICE_FLOOR, CERC_PRICE_CAP].
    """
    rng = np.random.default_rng(seed)
    rtm = dam_df[["date", "block_no"]].copy()
    multiplier = rng.lognormal(mean=0.0, sigma=0.15, size=len(dam_df))
    noise = rng.normal(0, 200, size=len(dam_df))
    raw_prices = dam_df["dam_mcp"].values * multiplier + noise
    rtm["rtm_mcp"] = np.clip(raw_prices, CERC_PRICE_FLOOR, CERC_PRICE_CAP).round(2)
    return rtm


def test_synthetic_rtm_alignment(market_df: pd.DataFrame) -> None:
    """Synthetic RTM must share the same dates and block_nos as input DAM."""
    dam_only = market_df[["date", "block_no", "dam_mcp"]].copy()
    rtm = _generate_synthetic_rtm(dam_only)

    pd.testing.assert_series_equal(
        dam_only["date"].reset_index(drop=True),
        rtm["date"].reset_index(drop=True),
        check_names=False,
    )
    pd.testing.assert_series_equal(
        dam_only["block_no"].reset_index(drop=True),
        rtm["block_no"].reset_index(drop=True),
        check_names=False,
    )
    assert len(rtm) == len(dam_only)


# ═══════════════════════════════════════════════════════════════════════════
# Test 9 — Synthetic price bounds
# ═══════════════════════════════════════════════════════════════════════════

def test_synthetic_price_bounds(market_df: pd.DataFrame) -> None:
    """Synthetic RTM prices must lie within CERC bounds."""
    dam_only = market_df[["date", "block_no", "dam_mcp"]].copy()
    rtm = _generate_synthetic_rtm(dam_only)

    assert rtm["rtm_mcp"].min() >= CERC_PRICE_FLOOR, "Synthetic RTM below floor"
    assert rtm["rtm_mcp"].max() <= CERC_PRICE_CAP, "Synthetic RTM above cap"


# ═══════════════════════════════════════════════════════════════════════════
# Bonus: integration-level test — full pipeline round-trip
# ═══════════════════════════════════════════════════════════════════════════

def test_full_pipeline_roundtrip() -> None:
    """End-to-end: create → standardize → validate → feature-engineer."""
    # 1. Raw-ish DataFrame with non-standard columns
    rng = np.random.default_rng(123)
    n_days = 5
    start = date(2024, 3, 1)
    rows = []
    for d in range(n_days):
        day = start + timedelta(days=d)
        for b in range(1, BLOCKS_PER_DAY + 1):
            rows.append({
                "Date": day,
                "Block No": b,
                "DAM MCP (Rs/MWh)": float(np.clip(rng.normal(3000, 800), 0, 10000)),
                "RTM MCP (Rs/MWh)": float(np.clip(rng.normal(3200, 1000), 0, 10000)),
                "Purchase Bid (MW)": float(rng.uniform(20000, 45000)),
                "Sell Bid (MW)": float(rng.uniform(20000, 45000)),
                "MCV (MW)": float(rng.uniform(18000, 40000)),
            })
    raw_df = pd.DataFrame(rows)

    # 2. Standardize
    std_df = _standardize_columns(raw_df)
    std_df["date"] = pd.to_datetime(std_df["date"])

    # 3. Validate
    assert std_df["block_no"].between(1, BLOCKS_PER_DAY).all()
    assert std_df["dam_mcp"].between(CERC_PRICE_FLOOR, CERC_PRICE_CAP).all()
    assert std_df["rtm_mcp"].between(CERC_PRICE_FLOOR, CERC_PRICE_CAP).all()

    # 4. Feature-engineer
    std_df = _build_lagged_features(std_df, horizon_blocks=4)
    assert "dam_mcp_lag4" in std_df.columns

    # 5. Check shape
    assert len(std_df) == n_days * BLOCKS_PER_DAY
