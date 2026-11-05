# -*- coding: utf-8 -*-
"""Market operator and trader risk metrics.

Translates quantile price forecasts and spike probabilities into
actionable risk indicators for trading desks and market operators.

Key Metrics
-----------
* **Market Clearing Risk Index (MCRI)** — 0–100 composite score
* **Value at Risk (VaR)** — P95 predicted MCP
* **Expected Shortfall (ES)** — tail-mean above VaR
* **Regime classification** — CALM / VOLATILE / ACUTE_SCARCITY
"""

from __future__ import annotations

from typing import Any, Dict, Literal

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Regime thresholds (MCRI 0–100 scale)
# ---------------------------------------------------------------------------
_REGIME_CALM_UPPER: float = 30.0
_REGIME_VOLATILE_UPPER: float = 70.0


class MarketRiskView:
    """Market-operator / trader translation layer.

    Parameters
    ----------
    quantile_forecasts_df : pd.DataFrame
        Columns must include quantile labels such as ``'q10'``, ``'q25'``,
        ``'q50'``, ``'q75'``, ``'q90'``.  Each row represents a 15-min
        time-block forecast (up to 96 rows for a full day).
    spike_probabilities : np.ndarray | pd.Series
        Per-block probability of an RTM price spike (0–1).  Length must
        match the number of rows in *quantile_forecasts_df*.
    """

    # Quantile column names expected in the DataFrame
    _Q_COLS: tuple[str, ...] = ("q10", "q25", "q50", "q75", "q90")

    def __init__(
        self,
        quantile_forecasts_df: pd.DataFrame,
        spike_probabilities: np.ndarray | pd.Series,
    ) -> None:
        df_clean = quantile_forecasts_df.copy()
        # Normalize column aliases like q_10 -> q10
        alias_map = {
            "q_10": "q10", "q_25": "q25", "q_50": "q50", "q_75": "q75", "q_90": "q90", "q_99": "q99",
            "0.1": "q10", "0.25": "q25", "0.5": "q50", "0.75": "q75", "0.9": "q90", "0.99": "q99"
        }
        df_clean.rename(columns={k: v for k, v in alias_map.items() if k in df_clean.columns}, inplace=True)
        # If q25 or q75 missing, interpolate
        if "q25" not in df_clean.columns and "q10" in df_clean.columns and "q50" in df_clean.columns:
            df_clean["q25"] = (df_clean["q10"] + df_clean["q50"]) / 2.0
        if "q75" not in df_clean.columns and "q50" in df_clean.columns and "q90" in df_clean.columns:
            df_clean["q75"] = (df_clean["q50"] + df_clean["q90"]) / 2.0

        self._validate_inputs(df_clean, spike_probabilities)

        self.forecasts: pd.DataFrame = df_clean
        self.spike_prob: np.ndarray = np.asarray(spike_probabilities, dtype=np.float64)

        # Pre-compute percentile ranks for composite score
        self._price_pctile: float = self._compute_price_percentile()
        self._vol_pctile: float = self._compute_volatility_percentile()

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    def _validate_inputs(
        self,
        df: pd.DataFrame,
        sp: np.ndarray | pd.Series,
    ) -> None:
        """Ensure inputs have the expected structure."""
        missing_cols = [c for c in self._Q_COLS if c not in df.columns]
        if missing_cols:
            raise ValueError(
                f"quantile_forecasts_df is missing columns: {missing_cols}. "
                f"Expected: {self._Q_COLS}"
            )
        if len(df) != len(sp):
            raise ValueError(
                f"Length mismatch: forecasts has {len(df)} rows but "
                f"spike_probabilities has {len(sp)} elements."
            )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _compute_price_percentile(self) -> float:
        """Median forecast as a percentile of the CERC price cap.

        Returns a value in [0, 1] where 1.0 ≡ Rs 10,000/MWh cap.
        """
        cerc_cap: float = 10_000.0  # Rs/MWh
        median_price: float = float(self.forecasts["q50"].mean())
        return min(median_price / cerc_cap, 1.0)

    def _compute_volatility_percentile(self) -> float:
        """Inter-quantile range (P90–P10) normalised to [0, 1].

        Uses the maximum observed IQR across blocks, normalised by the
        CERC price cap.
        """
        cerc_cap: float = 10_000.0
        iqr: pd.Series = self.forecasts["q90"] - self.forecasts["q10"]
        max_iqr: float = float(iqr.max())
        return min(max_iqr / cerc_cap, 1.0)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def compute_risk_index(self) -> float:
        """Market Clearing Risk Index (MCRI).

        Composite 0–100 score blending spike probability, price level,
        and forecast volatility:

        .. math::

            MCRI = 100 \\times (0.60 \\cdot \\bar{P}_{\\text{spike}}
                               + 0.25 \\cdot \\text{price\\_pctile}
                               + 0.15 \\cdot \\text{vol\\_pctile})

        Returns
        -------
        float
            Risk index in [0, 100].
        """
        mean_spike_prob: float = float(np.mean(self.spike_prob))
        risk: float = 100.0 * (
            0.60 * mean_spike_prob
            + 0.25 * self._price_pctile
            + 0.15 * self._vol_pctile
        )
        return round(float(np.clip(risk, 0.0, 100.0)), 2)

    def compute_var(self, confidence: float = 0.95) -> float:
        """Value at Risk from quantile forecasts.

        For the default 95 % confidence level this returns the mean of
        the P90 quantile forecast across all blocks (the highest
        available quantile that approximates P95).

        Parameters
        ----------
        confidence : float, default 0.95
            Confidence level.  Only 0.95 (→ q90) and 0.75 (→ q75) are
            natively supported; others linearly interpolate.

        Returns
        -------
        float
            VaR in Rs/MWh.
        """
        if confidence >= 0.95:
            return float(self.forecasts["q90"].mean())
        if confidence >= 0.75:
            # Linear interpolation between q75 and q90
            alpha = (confidence - 0.75) / 0.20
            return float(
                (1 - alpha) * self.forecasts["q75"].mean()
                + alpha * self.forecasts["q90"].mean()
            )
        return float(self.forecasts["q50"].mean())

    def compute_expected_shortfall(self, confidence: float = 0.95) -> float:
        """Expected Shortfall (Conditional VaR).

        Mean of all quantile predictions that exceed the VaR threshold.

        Parameters
        ----------
        confidence : float, default 0.95
            Confidence level for the underlying VaR.

        Returns
        -------
        float
            ES in Rs/MWh.  Returns the VaR itself when no quantile
            predictions exceed it.
        """
        var: float = self.compute_var(confidence)

        # Gather all quantile values across blocks
        q_values: np.ndarray = self.forecasts[list(self._Q_COLS)].values.ravel()
        tail: np.ndarray = q_values[q_values >= var]

        if tail.size == 0:
            return var  # Fallback — VaR is the tail boundary
        return float(np.mean(tail))

    def classify_regime(
        self,
    ) -> Literal["CALM", "VOLATILE", "ACUTE_SCARCITY"]:
        """Classify the current market regime.

        Returns
        -------
        {'CALM', 'VOLATILE', 'ACUTE_SCARCITY'}
            Based on MCRI thresholds: 0–30 → CALM, 30–70 → VOLATILE,
            70–100 → ACUTE_SCARCITY.
        """
        ri: float = self.compute_risk_index()
        if ri < _REGIME_CALM_UPPER:
            return "CALM"
        if ri < _REGIME_VOLATILE_UPPER:
            return "VOLATILE"
        return "ACUTE_SCARCITY"

    def summary(self) -> Dict[str, Any]:
        """Return a dictionary with all market-risk metrics.

        Keys
        ----
        risk_index : float
        var : float
        es : float
        regime : str
        spike_prob : float  (mean across blocks)
        """
        return {
            "risk_index": self.compute_risk_index(),
            "var": round(self.compute_var(), 2),
            "es": round(self.compute_expected_shortfall(), 2),
            "regime": self.classify_regime(),
            "spike_prob": round(float(np.mean(self.spike_prob)), 4),
        }
