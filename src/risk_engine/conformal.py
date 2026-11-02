"""
Conformal Prediction Intervals for Distribution-Free Electricity Price Forecasting.

Provides finite-sample coverage guarantees without assuming normality or homoskedasticity.
Uses Split Conformal Prediction (inductive conformal prediction) with CERC boundary clipping.
"""

from __future__ import annotations

import logging
from typing import Dict, Optional, Tuple, Union

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor

logger = logging.getLogger(__name__)


class ConformalPredictor:
    """
    Split Conformal Prediction wrapper for point regressors.
    Guarantees at least 1 - alpha empirical coverage under exchangeability.
    """

    def __init__(
        self,
        base_model: Optional[object] = None,
        alpha: float = 0.10,
        cal_fraction: float = 0.20,
        price_floor: float = 0.0,
        price_cap: float = 10000.0,
    ):
        self.alpha = alpha
        self.cal_fraction = cal_fraction
        self.price_floor = price_floor
        self.price_cap = price_cap

        if base_model is None:
            self.base_model = GradientBoostingRegressor(
                n_estimators=150,
                max_depth=5,
                learning_rate=0.05,
                random_state=42,
            )
        else:
            self.base_model = base_model

        self.conformal_quantile: float = 0.0
        self.is_fitted: bool = False

    def fit(
        self,
        X_train: Union[pd.DataFrame, np.ndarray],
        y_train: Union[pd.Series, np.ndarray],
    ) -> "ConformalPredictor":
        """
        Fits the base model on the proper training set, and computes conformal
        nonconformity scores on the held-out calibration set.
        """
        X = np.asarray(X_train)
        y = np.asarray(y_train).ravel()

        n_samples = len(X)
        n_cal = max(50, int(n_samples * self.cal_fraction))
        n_proper = n_samples - n_cal

        # Strict temporal split: proper training on earlier period, calibration on recent period
        X_proper, y_proper = X[:n_proper], y[:n_proper]
        X_cal, y_cal = X[n_proper:], y[n_proper:]

        self.base_model.fit(X_proper, y_proper)

        # Nonconformity scores: absolute residuals on calibration set
        y_cal_pred = self.base_model.predict(X_cal)
        scores = np.abs(y_cal - y_cal_pred)

        # Conformal quantile level with finite sample adjustment: (1 - alpha) * (1 + 1 / n_cal)
        quantile_level = min(1.0, (1.0 - self.alpha) * (1.0 + 1.0 / n_cal))
        self.conformal_quantile = float(np.quantile(scores, quantile_level))

        self.is_fitted = True
        return self

    def predict_interval(
        self,
        X_test: Union[pd.DataFrame, np.ndarray],
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Returns (lower_bound, point_prediction, upper_bound) with 1 - alpha coverage.
        """
        if not self.is_fitted:
            raise RuntimeError("Model has not been fitted yet.")

        X = np.asarray(X_test)
        point_pred = self.base_model.predict(X)

        lower = np.maximum(self.price_floor, point_pred - self.conformal_quantile)
        upper = np.minimum(self.price_cap, point_pred + self.conformal_quantile)

        return lower, point_pred, upper

    def evaluate(
        self,
        X_test: Union[pd.DataFrame, np.ndarray],
        y_test: Union[pd.Series, np.ndarray],
    ) -> Dict[str, float]:
        """
        Evaluates empirical coverage rate and mean interval width on test data.
        """
        y_true = np.asarray(y_test).ravel()
        lower, median, upper = self.predict_interval(X_test)
        return evaluate_coverage(y_true, lower, upper)


def evaluate_coverage(
    y_true: Union[pd.Series, np.ndarray],
    lower: Union[pd.Series, np.ndarray],
    upper: Union[pd.Series, np.ndarray],
) -> Dict[str, float]:
    """
    Computes coverage percentage and average interval width.
    """
    y = np.asarray(y_true).ravel()
    low = np.asarray(lower).ravel()
    up = np.asarray(upper).ravel()

    covered = (y >= low) & (y <= up)
    coverage_rate = float(np.mean(covered))
    avg_width = float(np.mean(up - low))

    return {
        "empirical_coverage": coverage_rate,
        "average_interval_width": avg_width,
        "sample_count": len(y),
    }
