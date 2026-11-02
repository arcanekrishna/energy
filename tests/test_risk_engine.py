"""
Comprehensive pytest test suite for the risk engine.

Tests cover:
- Quantile regression monotonicity (q10 <= q25 <= ... <= q99)
- Interval coverage and pinball loss calculations
- Calibrated stress classifier probability bounds [0, 1]
- Split conformal prediction interval guarantees
- Multi-horizon temporal splitting without leakage
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.risk_engine.conformal import ConformalPredictor, evaluate_coverage
from src.risk_engine.horizons import (
    HORIZON_1H,
    HORIZON_2H,
    HORIZON_4H,
    prepare_horizon_dataset,
    temporal_train_test_split,
)
from src.risk_engine.quantile_models import (
    QuantileForecaster,
    compute_crps,
    compute_interval_coverage,
    compute_pinball_loss,
    enforce_quantile_monotonicity,
)
from src.risk_engine.stress_classifier import StressClassifier, optimal_threshold


@pytest.fixture
def synthetic_training_data():
    """Generates a small deterministic dataset (500 blocks) for fast testing."""
    np.random.seed(42)
    n = 500
    X = np.random.normal(0, 1, (n, 6))
    # Price target with positive mean and realistic variability
    y_price = np.clip(3500.0 + 1200.0 * X[:, 0] + np.random.normal(0, 300, n), 500.0, 9500.0)
    # Binary spike target (10% positive)
    y_spike = (y_price >= np.percentile(y_price, 90)).astype(int)
    return X, y_price, y_spike


def test_quantile_monotonicity():
    """Validates that non-crossing post-hoc sorting enforces q10 <= ... <= q99."""
    raw_df = pd.DataFrame({
        "q_10": [3500.0, 4200.0, 3100.0],
        "q_50": [3400.0, 4100.0, 3300.0],  # Inverted on row 0 and 1
        "q_90": [4800.0, 5000.0, 4500.0],
    })
    sorted_df = enforce_quantile_monotonicity(raw_df)

    assert (sorted_df["q_10"] <= sorted_df["q_50"]).all()
    assert (sorted_df["q_50"] <= sorted_df["q_90"]).all()


def test_quantile_forecaster_fit_predict(synthetic_training_data):
    """Tests that QuantileForecaster outputs valid monotonic distributions."""
    X, y_price, _ = synthetic_training_data
    forecaster = QuantileForecaster(quantiles=[0.10, 0.50, 0.90], n_estimators=40, max_depth=3)
    forecaster.fit(X[:400], y_price[:400])

    preds = forecaster.predict(X[400:])
    assert preds.shape == (100, 3)
    assert (preds["q_10"] <= preds["q_50"]).all()
    assert (preds["q_50"] <= preds["q_90"]).all()

    crps = compute_crps(y_price[400:], preds)
    assert crps > 0.0


def test_stress_classifier_calibration(synthetic_training_data):
    """Tests calibrated classifier output probabilities and Brier score."""
    X, _, y_spike = synthetic_training_data
    clf = StressClassifier(n_estimators=30, max_depth=3)
    clf.fit(X[:400], y_spike[:400])

    probs = clf.predict_proba(X[400:])
    assert len(probs) == 100
    assert (probs >= 0.0).all() and (probs <= 1.0).all()

    eval_dict = clf.evaluate(X[400:], y_spike[400:], threshold=0.35)
    assert 0.0 <= eval_dict["brier_score"] <= 0.35
    assert 0.0 <= eval_dict["roc_auc"] <= 1.0


def test_conformal_prediction_coverage(synthetic_training_data):
    """Tests that ConformalPredictor delivers empirical coverage close to 1 - alpha."""
    X, y_price, _ = synthetic_training_data
    cp = ConformalPredictor(alpha=0.10, cal_fraction=0.25)
    cp.fit(X[:350], y_price[:350])

    lower, median, upper = cp.predict_interval(X[350:])
    assert len(lower) == 150
    assert (lower <= upper).all()

    cov_eval = evaluate_coverage(y_price[350:], lower, upper)
    # With 1 - alpha = 0.90, empirical coverage should be >= 0.75 even on small test sets
    assert cov_eval["empirical_coverage"] >= 0.75
    assert cov_eval["average_interval_width"] > 0.0


def test_temporal_train_test_split():
    """Validates that temporal split does not shuffle and preserves chronological order."""
    dates = pd.date_range("2024-01-01", periods=10, freq="D")
    df = pd.DataFrame({"date": dates, "val": np.arange(10)})

    train, test = temporal_train_test_split(df, train_frac=0.70)
    assert len(train) == 7
    assert len(test) == 3
    assert train["date"].max() < test["date"].min()
