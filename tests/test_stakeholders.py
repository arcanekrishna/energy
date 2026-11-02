"""
Comprehensive pytest test suite for stakeholder translation modules.

Tests cover:
- Market risk index, VaR, Expected Shortfall, and regime transitions
- Grid supply-demand pressure index and net demand ramp alerts
- Procurement strategy recommendations and downside exposure calculations
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.stakeholders.grid_view import GridRiskView
from src.stakeholders.market_view import MarketRiskView
from src.stakeholders.procurement_view import ProcurementRiskView


def test_market_risk_view():
    """Tests market operator risk index and regime bounds."""
    # Synthetic quantile predictions (10 blocks)
    q_df = pd.DataFrame({
        "q_10": [2500.0] * 10,
        "q_50": [3500.0] * 10,
        "q_90": [7500.0] * 10,
        "q_99": [9200.0] * 10,
    })
    spike_probs = np.array([0.10, 0.15, 0.20, 0.75, 0.85, 0.80, 0.30, 0.20, 0.10, 0.05])

    view = MarketRiskView(quantile_forecasts_df=q_df, spike_probabilities=spike_probs)
    risk_index = view.compute_risk_index()
    assert 0.0 <= risk_index <= 100.0

    var_95 = view.compute_var(confidence=0.95)
    es_95 = view.compute_expected_shortfall(confidence=0.95)
    assert var_95 > 0.0
    assert es_95 >= var_95

    regime = view.classify_regime()
    assert regime in ("CALM", "VOLATILE", "ACUTE_SCARCITY")


def test_grid_risk_view():
    """Tests grid operator pressure index and ramping warnings."""
    # Test block slice with high ramping
    block_slice = pd.DataFrame({
        "block_no": np.arange(70, 75),
        "dam_purchase_bid": [8500.0, 9200.0, 10500.0, 11800.0, 12000.0],
        "dam_sell_bid": [7000.0, 6800.0, 6500.0, 6200.0, 6000.0],
        "rtm_sell_bid": [1200.0, 1100.0, 900.0, 800.0, 700.0],
        "rtm_purchase_bid": [2500.0, 2800.0, 3200.0, 3500.0, 3600.0],
    })

    grid_view = GridRiskView(df_market_block=block_slice)
    pressure = grid_view.compute_supply_demand_pressure()
    assert 0.0 <= pressure <= 100.0

    ramp_info = grid_view.compute_ramp_warning()
    assert "alert_level" in ramp_info
    assert ramp_info["alert_level"] in ("NORMAL", "WATCH", "WARNING", "CRITICAL")


def test_procurement_risk_view():
    """Tests Discom procurement spread forecast and hedging strategy."""
    dam_prices = np.array([4000.0] * 5)
    # RTM projected significantly higher (median ₹5500/MWh)
    rtm_quantiles = pd.DataFrame({
        "q_10": [4200.0] * 5,
        "q_50": [5500.0] * 5,
        "q_90": [8500.0] * 5,
    })
    spike_p = np.array([0.65] * 5)

    proc_view = ProcurementRiskView(
        dam_prices=dam_prices,
        rtm_forecast_quantiles=rtm_quantiles,
        spike_probabilities=spike_p,
    )

    rec = proc_view.compute_strategy_recommendation()
    assert rec["strategy"] == "LOCK_DAM"
    assert rec["confidence"] > 0.50

    exp = proc_view.compute_exposure_rs(unhedged_mw=50.0)
    assert exp["expected_additional_cost_lakhs"] > 0.0
    assert exp["tail_risk_p90_cost_lakhs"] >= exp["expected_additional_cost_lakhs"]
