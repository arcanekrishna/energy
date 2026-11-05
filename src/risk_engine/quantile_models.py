"""
Quantile regression forecasting for Indian electricity price distributions.

Uses LightGBM's native ``quantile`` objective for efficient, accurate quantile
estimation.  Falls back to scikit-learn's ``GradientBoostingRegressor`` with
``loss='quantile'`` when LightGBM is unavailable.

Key metrics implemented:
- **CRPS** (Continuous Ranked Probability Score) — scalar summary of full
  predictive distribution quality.
- **Pinball / quantile loss** — per-quantile calibration metric.
- **Interval coverage** — empirical coverage of prediction intervals.

Indian Electricity Market Context
----------------------------------
- CERC price cap: ₹10,000/MWh (₹10/kWh).
- Extreme right tail matters: quantile 0.99 captures spike risk.
"""

from __future__ import annotations

import logging
import warnings
from typing import Dict, List, Optional, Sequence, Tuple, Union

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# LightGBM with sklearn fallback
# ---------------------------------------------------------------------------

try:
    import lightgbm as lgb

    _HAS_LIGHTGBM = True
    logger.debug("LightGBM available — using native quantile objective.")
except ImportError:
    _HAS_LIGHTGBM = False
    logger.info(
        "LightGBM not installed; falling back to sklearn GradientBoostingRegressor."
    )

from sklearn.ensemble import GradientBoostingRegressor  # always available


# ---------------------------------------------------------------------------
# Quantile forecaster
# ---------------------------------------------------------------------------


class QuantileForecaster:
    """Multi-quantile price forecaster using gradient-boosted trees.

    Fits one model per requested quantile and returns a full predictive
    distribution summary at inference time.

    Parameters
    ----------
    quantiles : list[float], optional
        Quantile levels to estimate.  Defaults to
        ``[0.10, 0.25, 0.50, 0.75, 0.90, 0.99]``.

    Examples
    --------
    >>> qf = QuantileForecaster()
    >>> qf.fit(X_train, y_train)
    >>> preds = qf.predict(X_test)
    >>> preds.columns
    Index(['q_10', 'q_25', 'q_50', 'q_75', 'q_90', 'q_99'], dtype='object')
    """

    # Default hyper-parameters (shared across all quantile models).
    _DEFAULT_PARAMS: Dict[str, Union[int, float]] = {
        "n_estimators": 200,
        "max_depth": 6,
        "learning_rate": 0.05,
        "min_child_samples": 20,
        "subsample": 0.8,
    }

    def __init__(
        self,
        quantiles: Optional[List[float]] = None,
        model_params: Optional[Dict] = None,
        **kwargs,
    ) -> None:
        self.quantiles: List[float] = quantiles or [
            0.10, 0.25, 0.50, 0.75, 0.90, 0.99
        ]
        self._validate_quantiles()
        self.custom_params: Dict = model_params or {}
        self.custom_params.update(kwargs)
        self.models_: Dict[float, object] = {}
        self._fitted: bool = False

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #

    def _validate_quantiles(self) -> None:
        """Ensure quantile levels are in (0, 1) and sorted."""
        for q in self.quantiles:
            if not 0.0 < q < 1.0:
                raise ValueError(f"Quantile must be in (0, 1), got {q}")
        self.quantiles = sorted(self.quantiles)

    @staticmethod
    def _quantile_col_name(q: float) -> str:
        """Convert a quantile level to a column name, e.g. 0.10 → ``q_10``."""
        return f"q_{int(q * 100):02d}"

    def _build_model(self, quantile: float) -> object:
        """Instantiate a single quantile regression model.

        Uses LightGBM when available, else sklearn's GBR.
        """
        p = {**self._DEFAULT_PARAMS, **self.custom_params}
        if _HAS_LIGHTGBM:
            return lgb.LGBMRegressor(
                objective="quantile",
                alpha=quantile,
                n_estimators=int(p["n_estimators"]),
                max_depth=int(p["max_depth"]),
                learning_rate=float(p["learning_rate"]),
                min_child_samples=int(p["min_child_samples"]),
                subsample=float(p["subsample"]),
                random_state=42,
                verbose=-1,
                n_jobs=-1,
            )
        else:
            # sklearn fallback — API differences handled transparently.
            return GradientBoostingRegressor(
                loss="quantile",
                alpha=quantile,
                n_estimators=int(p["n_estimators"]),
                max_depth=int(p["max_depth"]),
                learning_rate=float(p["learning_rate"]),
                min_samples_leaf=int(p["min_child_samples"]),
                subsample=float(p["subsample"]),
                random_state=42,
            )

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def fit(
        self,
        X_train: Union[pd.DataFrame, np.ndarray],
        y_train: Union[pd.Series, np.ndarray],
    ) -> "QuantileForecaster":
        """Fit one gradient-boosted model per quantile.

        Parameters
        ----------
        X_train : array-like of shape (n_samples, n_features)
            Training feature matrix.
        y_train : array-like of shape (n_samples,)
            Training target (continuous price).

        Returns
        -------
        self
            Fitted forecaster (for method chaining).
        """
        X_arr = np.asarray(X_train, dtype=np.float64)
        y_arr = np.asarray(y_train, dtype=np.float64).ravel()

        if X_arr.shape[0] != y_arr.shape[0]:
            raise ValueError(
                f"X_train and y_train row count mismatch: "
                f"{X_arr.shape[0]} vs {y_arr.shape[0]}"
            )

        logger.info(
            "Fitting %d quantile models on %d samples, %d features.",
            len(self.quantiles),
            X_arr.shape[0],
            X_arr.shape[1],
        )

        self.models_ = {}
        for q in self.quantiles:
            model = self._build_model(q)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                model.fit(X_arr, y_arr)
            self.models_[q] = model
            logger.debug("  q=%.2f fitted.", q)

        self._fitted = True
        return self

    def predict(
        self,
        X: Union[pd.DataFrame, np.ndarray],
    ) -> pd.DataFrame:
        """Predict all quantiles for new observations.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Feature matrix.

        Returns
        -------
        pd.DataFrame
            Columns named ``q_10, q_25, …, q_99`` with predicted quantile
            values.  Post-hoc monotonicity is enforced.
        """
        self._check_fitted()
        X_arr = np.asarray(X, dtype=np.float64)

        results: Dict[str, np.ndarray] = {}
        for q in self.quantiles:
            col = self._quantile_col_name(q)
            results[col] = self.models_[q].predict(X_arr)

        pred_df = pd.DataFrame(results)
        pred_df = enforce_quantile_monotonicity(pred_df)
        return pred_df

    def predict_intervals(
        self,
        X: Union[pd.DataFrame, np.ndarray],
        lower: float = 0.10,
        upper: float = 0.90,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Predict a specific prediction interval plus the median.

        Parameters
        ----------
        X : array-like
            Feature matrix.
        lower : float, default 0.10
            Lower quantile level for the interval.
        upper : float, default 0.90
            Upper quantile level for the interval.

        Returns
        -------
        lower_bound : np.ndarray
            Predicted lower quantile values.
        median : np.ndarray
            Predicted median (q_50) values.
        upper_bound : np.ndarray
            Predicted upper quantile values.

        Raises
        ------
        ValueError
            If the requested quantile levels were not fitted.
        """
        self._check_fitted()

        for q in (lower, 0.50, upper):
            if q not in self.models_:
                raise ValueError(
                    f"Quantile {q} was not fitted. "
                    f"Available: {sorted(self.models_.keys())}"
                )

        X_arr = np.asarray(X, dtype=np.float64)
        lower_bound = self.models_[lower].predict(X_arr)
        median = self.models_[0.50].predict(X_arr)
        upper_bound = self.models_[upper].predict(X_arr)

        # Enforce ordering: lower <= median <= upper
        lower_bound = np.minimum(lower_bound, median)
        upper_bound = np.maximum(upper_bound, median)

        return lower_bound, median, upper_bound

    def _check_fitted(self) -> None:
        """Raise if the forecaster has not been fitted."""
        if not self._fitted:
            raise RuntimeError(
                "QuantileForecaster has not been fitted. Call .fit() first."
            )


# ---------------------------------------------------------------------------
# Post-processing & evaluation utilities
# ---------------------------------------------------------------------------


def enforce_quantile_monotonicity(predictions_df: pd.DataFrame) -> pd.DataFrame:
    """Enforce non-decreasing order across quantile columns row-wise.

    Gradient-boosted quantile models are fitted independently, so their
    predictions may occasionally violate monotonicity.  This function
    sorts each row's quantile values in ascending order.

    Parameters
    ----------
    predictions_df : pd.DataFrame
        DataFrame where each column is a quantile prediction (e.g.
        ``q_10, q_25, …, q_99``).

    Returns
    -------
    pd.DataFrame
        Same shape and column names, with row-wise monotonicity enforced.
    """
    cols = predictions_df.columns.tolist()
    values = predictions_df.values.copy()
    # np.sort along axis=1 is vectorised — no Python loop over rows.
    values_sorted = np.sort(values, axis=1)
    return pd.DataFrame(values_sorted, columns=cols, index=predictions_df.index)


def compute_crps(
    y_true: Union[pd.Series, np.ndarray],
    quantile_predictions: pd.DataFrame,
) -> float:
    """Approximate Continuous Ranked Probability Score (CRPS).

    Uses the quantile decomposition of CRPS as the mean pinball loss across
    quantile levels.  This is exact in the limit of infinitely many quantiles
    and provides a good approximation for the typical 6-quantile setup.

    .. math::

        \\text{CRPS} \\approx \\frac{2}{K} \\sum_{k=1}^{K}
            \\rho_{\\tau_k}(y - \\hat{q}_{\\tau_k})

    Parameters
    ----------
    y_true : array-like of shape (n_samples,)
        Observed values.
    quantile_predictions : pd.DataFrame
        Each column is a quantile prediction; column names encode the
        quantile level (e.g. ``q_10`` → 0.10).

    Returns
    -------
    float
        Mean CRPS across all observations.
    """
    y = np.asarray(y_true, dtype=np.float64).ravel()

    total_pinball = 0.0
    n_quantiles = 0

    for col in quantile_predictions.columns:
        # Parse quantile level from column name (e.g. "q_10" → 0.10).
        try:
            q_level = int(col.split("_")[1]) / 100.0
        except (IndexError, ValueError):
            logger.warning("Cannot parse quantile from column '%s'; skipping.", col)
            continue

        y_pred = np.asarray(quantile_predictions[col], dtype=np.float64)
        total_pinball += compute_pinball_loss(y, y_pred, q_level)
        n_quantiles += 1

    if n_quantiles == 0:
        raise ValueError("No valid quantile columns found in predictions DataFrame.")

    # Factor of 2 to convert mean pinball into CRPS approximation.
    return 2.0 * total_pinball / n_quantiles


def compute_pinball_loss(
    y_true: Union[pd.Series, np.ndarray],
    y_pred: Union[pd.Series, np.ndarray],
    quantile: float,
) -> float:
    """Compute pinball (quantile) loss.

    .. math::

        \\rho_\\tau(u) = u (\\tau - \\mathbb{1}_{u < 0})

    Parameters
    ----------
    y_true : array-like of shape (n_samples,)
        Observed values.
    y_pred : array-like of shape (n_samples,)
        Predicted quantile values.
    quantile : float
        Quantile level in (0, 1).

    Returns
    -------
    float
        Mean pinball loss.
    """
    if not 0.0 < quantile < 1.0:
        raise ValueError(f"Quantile must be in (0, 1), got {quantile}")

    y = np.asarray(y_true, dtype=np.float64).ravel()
    yhat = np.asarray(y_pred, dtype=np.float64).ravel()

    residuals = y - yhat
    loss = np.where(
        residuals >= 0,
        quantile * residuals,
        (quantile - 1.0) * residuals,
    )
    return float(np.mean(loss))


def compute_interval_coverage(
    y_true: Union[pd.Series, np.ndarray],
    lower: Union[pd.Series, np.ndarray],
    upper: Union[pd.Series, np.ndarray],
) -> float:
    """Compute empirical coverage rate of a prediction interval.

    Parameters
    ----------
    y_true : array-like of shape (n_samples,)
        Observed values.
    lower : array-like of shape (n_samples,)
        Lower bounds of the prediction interval.
    upper : array-like of shape (n_samples,)
        Upper bounds of the prediction interval.

    Returns
    -------
    float
        Fraction of observations falling within ``[lower, upper]``.
    """
    y = np.asarray(y_true, dtype=np.float64).ravel()
    lo = np.asarray(lower, dtype=np.float64).ravel()
    hi = np.asarray(upper, dtype=np.float64).ravel()

    if not (y.shape[0] == lo.shape[0] == hi.shape[0]):
        raise ValueError("All input arrays must have the same length.")

    covered = (y >= lo) & (y <= hi)
    return float(np.mean(covered))
