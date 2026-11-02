"""
Explainability and Feature Contribution Analysis for Indian Electricity Risk Forecasting.

Quantifies the predictive contribution of Day-Ahead Market (DAM) bidding indicators
versus Real-Time Market (RTM) lagged dynamics across different forecast lead times.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def compute_feature_importance(
    model: object,
    feature_names: List[str],
) -> pd.DataFrame:
    """
    Extracts normalized feature importances from a tree-based model.
    """
    if hasattr(model, "feature_importances_"):
        raw_importances = model.feature_importances_
    elif hasattr(model, "calibrated_model") and hasattr(model.calibrated_model, "calibrated_classifiers_"):
        # Average across calibrated folds
        imps = [clf.estimator.feature_importances_ for clf in model.calibrated_model.calibrated_classifiers_]
        raw_importances = np.mean(imps, axis=0)
    elif hasattr(model, "estimators_"):
        # Quantile forecaster dict or list
        if isinstance(model.estimators_, dict):
            # Take median model
            median_key = list(model.estimators_.keys())[len(model.estimators_) // 2]
            raw_importances = model.estimators_[median_key].feature_importances_
        else:
            raw_importances = np.mean([est.feature_importances_ for est in model.estimators_], axis=0)
    else:
        raw_importances = np.ones(len(feature_names)) / len(feature_names)

    # Normalize to percentage
    total = np.sum(raw_importances)
    norm_importances = raw_importances / total if total > 0 else raw_importances

    df = pd.DataFrame({
        "feature": feature_names,
        "importance": norm_importances,
    }).sort_values("importance", ascending=False).reset_index(drop=True)

    return df


def dam_vs_rtm_importance(importance_df: pd.DataFrame) -> Dict[str, float]:
    """
    Partitions feature importances into three core structural buckets:
    - DAM fundamental signals (dam_*)
    - RTM intraday signals (rtm_*)
    - Temporal / Grid regimes (sin_block, ramp, weekend, month, etc.)
    """
    dam_sum = 0.0
    rtm_sum = 0.0
    temporal_sum = 0.0

    for _, row in importance_df.iterrows():
        feat = str(row["feature"]).lower()
        val = float(row["importance"])

        if feat.startswith("dam_"):
            dam_sum += val
        elif feat.startswith("rtm_"):
            rtm_sum += val
        else:
            temporal_sum += val

    total = dam_sum + rtm_sum + temporal_sum
    if total > 0:
        return {
            "dam_share": dam_sum / total,
            "rtm_share": rtm_sum / total,
            "temporal_share": temporal_sum / total,
        }
    return {"dam_share": 0.33, "rtm_share": 0.33, "temporal_share": 0.34}


def compute_shap_values(
    model: object,
    X: Union[pd.DataFrame, np.ndarray],
    feature_names: List[str],
    max_samples: int = 300,
) -> Optional[pd.DataFrame]:
    """
    Attempts SHAP TreeExplainer calculation; returns DataFrame of mean absolute SHAP values.
    Falls back gracefully if shap is not installed.
    """
    try:
        import shap

        X_df = pd.DataFrame(X, columns=feature_names) if not isinstance(X, pd.DataFrame) else X
        sample_X = X_df.sample(min(len(X_df), max_samples), random_state=42)

        # Handle underlying estimators
        target_model = getattr(model, "base_model", model)
        explainer = shap.TreeExplainer(target_model)
        shap_vals = explainer.shap_values(sample_X)

        if isinstance(shap_vals, list):
            # Classification output: use positive class
            vals = shap_vals[1] if len(shap_vals) > 1 else shap_vals[0]
        else:
            vals = shap_vals

        mean_abs_shap = np.mean(np.abs(vals), axis=0)
        total = np.sum(mean_abs_shap)
        norm_shap = mean_abs_shap / total if total > 0 else mean_abs_shap

        df_shap = pd.DataFrame({
            "feature": feature_names,
            "mean_abs_shap": norm_shap,
        }).sort_values("mean_abs_shap", ascending=False).reset_index(drop=True)

        return df_shap
    except Exception as e:
        logger.warning(f"SHAP explanation skipped: {e}")
        return None
