# -*- coding: utf-8 -*-
"""Grid operator reliability metrics.

Translates market DataFrames into grid-reliability indicators relevant
to SLDC / RLDC control rooms:

* **Supply-Demand Pressure Index** — sigmoid-mapped imbalance ratio
* **Net-Demand Ramp Warning** — first-difference alert system
* **RTM Liquidity Alert** — sell-bid / purchase-bid coverage ratio
"""

from __future__ import annotations

from typing import Any, Dict, Literal

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Ramp-rate alert thresholds (MW / 15-min block)
# ---------------------------------------------------------------------------
_RAMP_WATCH: float = 500.0
_RAMP_WARNING: float = 1_000.0
_RAMP_CRITICAL: float = 2_000.0

# Liquidity drought threshold
_LIQUIDITY_DROUGHT: float = 0.5


def _sigmoid(x: np.ndarray | float) -> np.ndarray | float:
    """Numerically stable sigmoid function."""
    return 1.0 / (1.0 + np.exp(-np.clip(x, -500, 500)))


class GridRiskView:
    """Grid-operator translation layer.

    Parameters
    ----------
    df_market_block : pd.DataFrame
        A slice of the consolidated market DataFrame for the forecast
        window.  Expected columns (case-insensitive lookup attempted):

        * ``purchase_bid_dam`` or ``purchase_bid`` — DAM purchase bids (MW)
        * ``sell_bid_dam`` or ``sell_bid`` — DAM sell bids (MW)
        * ``rtm_purchase_bid`` — RTM purchase bids (MW)
        * ``rtm_sell_bid`` — RTM sell bids (MW)

        The DataFrame index or a ``block`` column should represent the
        15-min time-block number (1–96).
    """

    # Canonical column names (lowercase)
    _PURCHASE_COLS = ("purchase_bid_dam", "purchase_bid")
    _SELL_COLS = ("sell_bid_dam", "sell_bid")
    _RTM_PURCHASE_COLS = ("rtm_purchase_bid",)
    _RTM_SELL_COLS = ("rtm_sell_bid",)

    def __init__(self, df_market_block: pd.DataFrame) -> None:
        self.df: pd.DataFrame = df_market_block.copy()
        self._normalise_columns()
        self._resolve_columns()

    # ------------------------------------------------------------------
    # Column resolution helpers
    # ------------------------------------------------------------------
    def _normalise_columns(self) -> None:
        """Lower-case all column names for robust matching."""
        self.df.columns = [c.lower().strip() for c in self.df.columns]

    def _resolve(self, candidates: tuple[str, ...], label: str) -> str:
        """Return the first matching column name from *candidates*."""
        for c in candidates:
            if c in self.df.columns:
                return c
        raise KeyError(
            f"Cannot find '{label}' column. Tried: {candidates}. "
            f"Available: {list(self.df.columns)}"
        )

    def _resolve_columns(self) -> None:
        """Resolve actual column names once at init time."""
        self._col_purchase: str = self._resolve(self._PURCHASE_COLS, "purchase_bid")
        self._col_sell: str = self._resolve(self._SELL_COLS, "sell_bid")
        # RTM columns are optional — used only for liquidity alert
        try:
            self._col_rtm_purchase: str | None = self._resolve(
                self._RTM_PURCHASE_COLS, "rtm_purchase_bid"
            )
        except KeyError:
            self._col_rtm_purchase = None
        try:
            self._col_rtm_sell: str | None = self._resolve(
                self._RTM_SELL_COLS, "rtm_sell_bid"
            )
        except KeyError:
            self._col_rtm_sell = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def compute_supply_demand_pressure(self) -> float:
        """Supply-Demand Pressure Index (0–100).

        Based on the DAM imbalance ratio (purchase_bid / sell_bid):

        .. math::

            \\text{pressure} = 100 \\times \\sigma\\bigl(4 (r - 1)\\bigr)

        where *r* is the mean imbalance ratio and σ is the sigmoid
        function.  When purchase bids exactly equal sell bids (r = 1)
        the pressure sits at 50.  Higher values indicate demand
        exceeding supply.

        Returns
        -------
        float
            Pressure index clipped to [0, 100].
        """
        purchase: np.ndarray = self.df[self._col_purchase].values.astype(np.float64)
        sell: np.ndarray = self.df[self._col_sell].values.astype(np.float64)

        # Avoid division by zero — set zero-sell blocks to a tiny value
        sell_safe: np.ndarray = np.where(sell > 0, sell, 1.0)
        imbalance_ratio: float = float(np.mean(purchase / sell_safe))

        pressure: float = 100.0 * float(_sigmoid(4.0 * (imbalance_ratio - 1.0)))
        return round(float(np.clip(pressure, 0.0, 100.0)), 2)

    def compute_ramp_warning(
        self,
    ) -> Dict[str, float | Literal["NORMAL", "WATCH", "WARNING", "CRITICAL"]]:
        """Net-demand ramp rate and alert level.

        Computes the first difference of net demand
        (``purchase_bid − sell_bid``) across consecutive blocks and
        returns the maximum absolute ramp.

        Returns
        -------
        dict
            ``ramp_rate`` : float — max absolute ramp (MW / 15 min)
            ``alert_level`` : str — one of NORMAL, WATCH, WARNING, CRITICAL
        """
        net_demand: np.ndarray = (
            self.df[self._col_purchase].values.astype(np.float64)
            - self.df[self._col_sell].values.astype(np.float64)
        )
        ramp: np.ndarray = np.diff(net_demand)

        if ramp.size == 0:
            return {"ramp_rate": 0.0, "alert_level": "NORMAL"}

        max_ramp: float = float(np.max(np.abs(ramp)))

        if max_ramp >= _RAMP_CRITICAL:
            level: Literal["NORMAL", "WATCH", "WARNING", "CRITICAL"] = "CRITICAL"
        elif max_ramp >= _RAMP_WARNING:
            level = "WARNING"
        elif max_ramp >= _RAMP_WATCH:
            level = "WATCH"
        else:
            level = "NORMAL"

        return {"ramp_rate": round(max_ramp, 2), "alert_level": level}

    def compute_liquidity_alert(
        self,
    ) -> Dict[str, Any]:
        """RTM liquidity assessment.

        Ratio of RTM sell bids to RTM purchase bids.  If the ratio
        drops below 0.5 the market is in a **DROUGHT** condition —
        insufficient sell-side depth to clear purchases.

        Returns
        -------
        dict
            ``liquidity_ratio`` : float | None
            ``status`` : 'HEALTHY' | 'THIN' | 'DROUGHT' | 'UNAVAILABLE'
        """
        if self._col_rtm_sell is None or self._col_rtm_purchase is None:
            return {"liquidity_ratio": None, "status": "UNAVAILABLE"}

        rtm_sell: np.ndarray = self.df[self._col_rtm_sell].values.astype(np.float64)
        rtm_purchase: np.ndarray = self.df[self._col_rtm_purchase].values.astype(
            np.float64
        )

        total_purchase: float = float(np.sum(rtm_purchase))
        if total_purchase <= 0:
            return {"liquidity_ratio": 0.0, "status": "DROUGHT"}

        ratio: float = float(np.sum(rtm_sell)) / total_purchase

        if ratio < _LIQUIDITY_DROUGHT:
            status = "DROUGHT"
        elif ratio < 0.8:
            status = "THIN"
        else:
            status = "HEALTHY"

        return {"liquidity_ratio": round(ratio, 4), "status": status}

    def summary(self) -> Dict[str, Any]:
        """Consolidated grid-operator risk summary.

        Returns
        -------
        dict
            ``pressure_index`` : float
            ``ramp_warning`` : dict
            ``liquidity_status`` : dict
        """
        return {
            "pressure_index": self.compute_supply_demand_pressure(),
            "ramp_warning": self.compute_ramp_warning(),
            "liquidity_status": self.compute_liquidity_alert(),
        }
