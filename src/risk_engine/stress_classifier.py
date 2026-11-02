"""
Calibrated Probabilistic Market Stress Classifier for Indian Electricity Markets.

Predicts discrete market stress events (e.g. RTM price spikes >= P90 or >= ₹8/kWh)
with mathematically calibrated probability outputs.

Key components:
- Base Ensemble: GradientBoosting / HistGradientBoosting with class reweighting.
- Probability Calibration: Isotonic Regression / Platt Scaling on hold-out calibration fold.
- Reliability Diagrams: Empirical calibration curves and Brier Score evaluation.
- Threshold Optimization: Maximizing utility / F1-score for operational risk dispatch.
"""

from __future__ import annotations

import logging
from typing import Dict, Optional, Tuple, Union

import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import (
    brier_score_loss,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

logger = logging.getLogger(__name__)


class StressClassifier:
    """
    Calibrated probabilistic classifier for electricity market stress events.
    """

    def __init__(
        self,
        n_estimators: int = 150,
        max_depth: int = 4,
        learning_rate: float = 0.05,
        random_state: int = 42,
    ):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.learning_rate = learning_rate
        self.random_state = random_state
        self.base_model = GradientBoostingClassifier(
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
            learning_rate=self.learning_rate,
            random_state=self.random_state,
        )
        self.calibrated_model: Optional[CalibratedClassifierCV] = None
        self.is_fitted: bool = False

    def fit(self, X_train: Union[pd.DataFrame, np.ndarray], y_train: Union[pd.Series, np.ndarray]) -> "StressClassifier":
        """
        Fits the base tree model and calibrates probabilities using 3-fold CV.
        """
        X = np.asarray(X_train)
        y = np.asarray(y_train).ravel()

        if len(np.unique(y)) < 2:
            logger.warning("Only one class present in training data. Calibration will be degenerate.")

        self.calibrated_model = CalibratedClassifierCV(
            estimator=self.base_model,
            method="isotonic",
            cv=3,
        )
        self.calibrated_model.fit(X, y)
        self.is_fitted = True
        return self

    def predict_proba(self, X: Union[pd.DataFrame, np.ndarray]) -> np.ndarray:
        """
        Outputs well-calibrated probabilities P(Y=1).
        """
        if not self.is_fitted or self.calibrated_model is None:
            raise RuntimeError("Model has not been fitted yet.")
        X_arr = np.asarray(X)
        probs = self.calibrated_model.predict_proba(X_arr)
        # Return probability of positive class
        return probs[:, 1] if probs.shape[1] > 1 else probs[:, 0]

    def predict(self, X: Union[pd.DataFrame, np.ndarray], threshold: float = 0.35) -> np.ndarray:
        """
        Predicts binary event states based on an operational decision threshold.
        """
        probs = self.predict_proba(X)
        return (probs >= threshold).astype(int)

    def evaluate(
        self,
        X_test: Union[pd.DataFrame, np.ndarray],
        y_test: Union[pd.Series, np.ndarray],
        threshold: float = 0.35,
    ) -> Dict[str, float]:
        """
        Computes formal probabilistic and classification metrics.
        """
        y_true = np.asarray(y_test).ravel()
        probs = self.predict_proba(X_test)
        preds = (probs >= threshold).astype(int)

        # ROC-AUC requires both classes present in test set
        if len(np.unique(y_true)) > 1:
            auc = float(roc_auc_score(y_true, probs))
        else:
            auc = 0.50

        brier = float(brier_score_loss(y_true, probs))
        prec = float(precision_score(y_true, preds, zero_division=0))
        rec = float(recall_score(y_true, preds, zero_division=0))
        f1 = float(f1_score(y_true, preds, zero_division=0))

        # Expected Calibration Error (ECE) approximation
        prob_true, prob_pred = calibration_curve(y_true, probs, n_bins=10)
        ece = float(np.mean(np.abs(prob_true - prob_pred))) if len(prob_true) > 0 else 0.0

        return {
            "roc_auc": auc,
            "brier_score": brier,
            "precision": prec,
            "recall": rec,
            "f1_score": f1,
            "calibration_error": ece,
            "decision_threshold": threshold,
        }


def compute_calibration_curve(
    y_true: Union[pd.Series, np.ndarray],
    y_prob: Union[pd.Series, np.ndarray],
    n_bins: int = 10,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Computes reliability diagram data points (mean predicted probability vs true fraction).
    """
    y_t = np.asarray(y_true).ravel()
    y_p = np.asarray(y_prob).ravel()
    return calibration_curve(y_t, y_p, n_bins=n_bins, strategy="uniform")


def optimal_threshold(
    y_true: Union[pd.Series, np.ndarray],
    y_prob: Union[pd.Series, np.ndarray],
    metric: str = "f1",
) -> float:
    """
    Finds the optimal decision threshold via grid search over [0.10, 0.90].
    """
    y_t = np.asarray(y_true).ravel()
    y_p = np.asarray(y_prob).ravel()

    thresholds = np.linspace(0.10, 0.90, 81)
    best_score = -1.0
    best_th = 0.35

    for th in thresholds:
        preds = (y_p >= th).astype(int)
        if metric == "f1":
            score = f1_score(y_t, preds, zero_division=0)
        elif metric == "precision":
            score = precision_score(y_t, preds, zero_division=0)
        else:
            score = recall_score(y_t, preds, zero_division=0)

        if score > best_score:
            best_score = score
            best_th = float(th)

    return best_th
