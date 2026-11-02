"""
risk_engine — Multi-horizon probabilistic forecasting, calibrated classifiers,
conformal prediction intervals, and explainability for Indian electricity markets.
"""

try:
    from .horizons import (
        ALL_HORIZONS,
        HORIZON_1H,
        HORIZON_2H,
        HORIZON_4H,
        HORIZON_DAY_AHEAD,
        ForecastHorizon,
        prepare_horizon_dataset,
        temporal_train_test_split,
    )
    from .quantile_models import (
        QuantileForecaster,
        compute_crps,
        compute_interval_coverage,
        compute_pinball_loss,
        enforce_quantile_monotonicity,
    )
    from .stress_classifier import (
        StressClassifier,
        compute_calibration_curve,
        optimal_threshold,
    )
    from .conformal import (
        ConformalPredictor,
        evaluate_coverage,
    )
    from .explainability import (
        compute_feature_importance,
        compute_shap_values,
        dam_vs_rtm_importance,
    )
except ImportError:
    from src.risk_engine.horizons import (
        ALL_HORIZONS,
        HORIZON_1H,
        HORIZON_2H,
        HORIZON_4H,
        HORIZON_DAY_AHEAD,
        ForecastHorizon,
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
    from src.risk_engine.stress_classifier import (
        StressClassifier,
        compute_calibration_curve,
        optimal_threshold,
    )
    from src.risk_engine.conformal import (
        ConformalPredictor,
        evaluate_coverage,
    )
    from src.risk_engine.explainability import (
        compute_feature_importance,
        compute_shap_values,
        dam_vs_rtm_importance,
    )

__all__ = [
    # horizons
    "ForecastHorizon",
    "HORIZON_1H",
    "HORIZON_2H",
    "HORIZON_4H",
    "HORIZON_DAY_AHEAD",
    "ALL_HORIZONS",
    "prepare_horizon_dataset",
    "temporal_train_test_split",
    # quantile models
    "QuantileForecaster",
    "enforce_quantile_monotonicity",
    "compute_crps",
    "compute_pinball_loss",
    "compute_interval_coverage",
    # stress classifier
    "StressClassifier",
    "compute_calibration_curve",
    "optimal_threshold",
    # conformal
    "ConformalPredictor",
    "evaluate_coverage",
    # explainability
    "compute_feature_importance",
    "compute_shap_values",
    "dam_vs_rtm_importance",
]
