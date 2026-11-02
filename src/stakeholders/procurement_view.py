"""
Discom & Commercial Consumer Procurement Intelligence.

Translates DAM-RTM price spreads and risk probabilities into actionable
bidding and power procurement strategies:
- DAM vs RTM price spread forecasts.
- Optimal commitment timing (Lock volumes in Day-Ahead vs wait for Real-Time balancing).
- Financial downside exposure at risk (₹ Lakhs per hour) for unhedged open positions.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Literal, Optional, Union

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

StrategyType = Literal["LOCK_DAM", "HOLD_FOR_RTM", "SPLIT_PROCUREMENT"]


class ProcurementRiskView:
    """
    Power procurement translation layer for distribution companies (Discoms)
    and commercial & industrial (C&I) open access consumers.
    """

    def __init__(
        self,
        dam_prices: Union[pd.Series, np.ndarray, float],
        rtm_forecast_quantiles: Union[pd.DataFrame, Dict[str, float]],
        spike_probabilities: Optional[Union[pd.Series, np.ndarray, float]] = None,
    ):
        """
        Parameters
        ----------
        dam_prices : Series, ndarray, or float
            Known cleared Day-Ahead Market prices (₹/MWh).
        rtm_forecast_quantiles : DataFrame or Dict
            Quantile forecasts for RTM MCP (must contain 'q_10', 'q_50', 'q_90' or similar).
        spike_probabilities : Series, ndarray, or float, optional
            Estimated P(RTM Spike) for the target blocks.
        """
        self.dam_prices = np.atleast_1d(np.asarray(dam_prices, dtype=float))

        if isinstance(rtm_forecast_quantiles, dict):
            self.q_df = pd.DataFrame([rtm_forecast_quantiles])
        else:
            self.q_df = pd.DataFrame(rtm_forecast_quantiles)

        # Standardize quantile columns
        col_map = {}
        for c in self.q_df.columns:
            c_str = str(c).lower()
            if "10" in c_str:
                col_map[c] = "q_10"
            elif "50" in c_str:
                col_map[c] = "q_50"
            elif "90" in c_str:
                col_map[c] = "q_90"
        self.q_df.rename(columns=col_map, inplace=True)

        if spike_probabilities is not None:
            self.spike_probs = np.atleast_1d(np.asarray(spike_probabilities, dtype=float))
        else:
            self.spike_probs = np.zeros(len(self.dam_prices))

    def compute_spread_forecast(self) -> Dict[str, Any]:
        """
        Computes expected spread E[RTM] - DAM and forecast uncertainty range.
        """
        # E[RTM] approximated by median q_50 or mean of quantiles
        median_rtm = self.q_df["q_50"].values if "q_50" in self.q_df.columns else self.q_df.mean(axis=1).values
        expected_spread = median_rtm - self.dam_prices

        q90 = self.q_df["q_90"].values if "q_90" in self.q_df.columns else median_rtm * 1.3
        q10 = self.q_df["q_10"].values if "q_10" in self.q_df.columns else median_rtm * 0.7
        spread_uncertainty = q90 - q10

        return {
            "expected_spread_rs_mwh": float(np.mean(expected_spread)),
            "expected_spread_rs_kwh": float(np.mean(expected_spread) / 1000.0),
            "spread_uncertainty_rs_mwh": float(np.mean(spread_uncertainty)),
            "spread_series": expected_spread,
        }

    def compute_strategy_recommendation(self) -> Dict[str, Any]:
        """
        Determines the cost-optimal procurement decision based on spread expectation
        and tail risk penalty.
        """
        spread_info = self.compute_spread_forecast()
        mean_spread = spread_info["expected_spread_rs_mwh"]
        mean_spike_p = float(np.mean(self.spike_probs))

        # Decision rule:
        # If RTM is expected to be substantially more expensive (> ₹300/MWh) or spike risk is high (> 35%),
        # lock required volume in Day-Ahead.
        if mean_spread > 300.0 or mean_spike_p > 0.35:
            strategy: StrategyType = "LOCK_DAM"
            confidence = min(0.95, 0.60 + 0.35 * (mean_spike_p / 0.50))
            reason = (
                f"High risk of Real-Time price premium (Expected spread: +₹{mean_spread/1000:.2f}/kWh, "
                f"Spike prob: {mean_spike_p*100:.1f}%). Lock base and peak requirements in Day-Ahead Market."
            )
        elif mean_spread < -400.0 and mean_spike_p < 0.15:
            strategy = "HOLD_FOR_RTM"
            confidence = min(0.90, 0.65 + 0.25 * (abs(mean_spread) / 1500.0))
            reason = (
                f"Real-Time Market projected cheaper by ₹{abs(mean_spread)/1000:.2f}/kWh with low stress probability "
                f"({mean_spike_p*100:.1f}%). Hold flexible/balancing volume for RTM execution."
            )
        else:
            strategy = "SPLIT_PROCUREMENT"
            confidence = 0.70
            reason = (
                f"Moderate spread differential (₹{mean_spread/1000:.2f}/kWh). Recommend splitting portfolio: "
                "hedge 70-80% in DAM and procure residual 20-30% opportunistically in RTM."
            )

        return {
            "strategy": strategy,
            "confidence": float(confidence),
            "reason": reason,
        }

    def compute_exposure_rs(self, unhedged_mw: float = 100.0) -> Dict[str, float]:
        """
        Calculates financial exposure in ₹ Lakhs for an open position left to RTM.
        """
        median_rtm = self.q_df["q_50"].values if "q_50" in self.q_df.columns else self.dam_prices
        q90_rtm = self.q_df["q_90"].values if "q_90" in self.q_df.columns else median_rtm * 1.3

        # Downside per MWh: max(0, RTM - DAM)
        expected_adverse = np.maximum(0.0, median_rtm - self.dam_prices)
        p90_adverse = np.maximum(0.0, q90_rtm - self.dam_prices)

        # Total exposure for unhedged MW over the window (Rs to Rs Lakhs conversion: / 100,000)
        # unhedged_mw * 0.25h * adverse_rs_per_mwh / 100,000 per block
        exp_expected_lakhs = float(np.sum(unhedged_mw * 0.25 * expected_adverse) / 100000.0)
        exp_p90_lakhs = float(np.sum(unhedged_mw * 0.25 * p90_adverse) / 100000.0)

        return {
            "unhedged_mw": float(unhedged_mw),
            "expected_additional_cost_lakhs": exp_expected_lakhs,
            "tail_risk_p90_cost_lakhs": exp_p90_lakhs,
        }

    def summary(self, unhedged_mw: float = 100.0) -> Dict[str, Any]:
        """
        Returns full procurement executive intelligence summary.
        """
        spread = self.compute_spread_forecast()
        rec = self.compute_strategy_recommendation()
        exp = self.compute_exposure_rs(unhedged_mw=unhedged_mw)

        return {
            "strategy": rec["strategy"],
            "confidence": rec["confidence"],
            "reason": rec["reason"],
            "expected_spread_rs_kwh": spread["expected_spread_rs_kwh"],
            "spread_uncertainty_rs_mwh": spread["spread_uncertainty_rs_mwh"],
            "financial_exposure": exp,
        }
