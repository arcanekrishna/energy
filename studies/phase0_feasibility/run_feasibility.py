"""
Standalone Phase 0 Feasibility Study Runner.

Executes formal econometric and statistical tests to establish whether:
"Does the behaviour of the Day-Ahead Market contain early information about
market stress that subsequently emerges in the Real-Time Market?"

Usage:
------
    python -m studies.phase0_feasibility.run_feasibility
    # or
    python studies/phase0_feasibility/run_feasibility.py
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import brier_score_loss, precision_score, recall_score, roc_auc_score

try:
    from src.data_pipeline.feature_engine import build_features, get_feature_columns
    from src.data_pipeline.synthetic_generator import generate_full_synthetic
except ImportError:
    from indian_power_market.src.data_pipeline.feature_engine import build_features, get_feature_columns
    from indian_power_market.src.data_pipeline.synthetic_generator import generate_full_synthetic

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("phase0_study")


def run_phase0_study(data_path: str = None, output_dir: str = None) -> dict:
    """
    Executes the 4 hypothesis tests and outputs diagnostic reports and figures.
    """
    if output_dir is None:
        output_dir = Path(__file__).resolve().parent / "figures"
    else:
        output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load or Generate Dataset
    if data_path and os.path.exists(data_path):
        logger.info(f"Loading dataset from: {data_path}")
        df = pd.read_csv(data_path)
    else:
        logger.info("No external dataset specified. Generating 1-year calibrated benchmark (35,040 blocks)...")
        df = generate_full_synthetic(start_date="2024-01-01", days=365, seed=42)

    logger.info(f"Dataset active: {len(df):,} settlement blocks.")

    # Canonicalize metrics
    if "dam_imbalance_ratio" not in df.columns:
        df["dam_imbalance_ratio"] = df["dam_purchase_bid_mw"] / np.maximum(df["dam_sell_bid_mw"], 1.0)
    if "dam_rtm_spread" not in df.columns:
        df["dam_rtm_spread"] = df["rtm_mcp"] - df["dam_mcp"]

    rtm_p90 = df["rtm_mcp"].quantile(0.90)
    df["rtm_spike"] = (df["rtm_mcp"] >= rtm_p90).astype(int)

    # -----------------------------------------------------------------------
    # Hypothesis 1: DAM Imbalance -> RTM Price Spike (Contingency Analysis)
    # -----------------------------------------------------------------------
    logger.info("Testing Hypothesis 1: DAM Imbalance to RTM Spike Propagation...")
    high_dam_imb = (df["dam_imbalance_ratio"] >= df["dam_imbalance_ratio"].quantile(0.75))
    contingency = pd.crosstab(high_dam_imb, df["rtm_spike"])

    odds_ratio, p_val_fisher = stats.fisher_exact(contingency)
    point_biserial, p_val_corr = stats.pointbiserialr(df["dam_imbalance_ratio"], df["rtm_spike"])

    logger.info(f"  -> Odds Ratio: {odds_ratio:.2f} (p-value: {p_val_fisher:.4e})")
    logger.info(f"  -> Point-Biserial Correlation: {point_biserial:.3f}")

    # -----------------------------------------------------------------------
    # Hypothesis 2: Extreme DAM Clearance -> RTM Volatility Clustering
    # -----------------------------------------------------------------------
    logger.info("Testing Hypothesis 2: Price Clearance & Volatility Persistence...")
    dam_p80 = df["dam_mcp"].quantile(0.80)
    high_dam_mask = df["dam_mcp"] >= dam_p80

    df["rtm_roll_volat"] = df["rtm_mcp"].rolling(8).std().fillna(0.0)
    volat_high_dam = df.loc[high_dam_mask, "rtm_roll_volat"]
    volat_norm_dam = df.loc[~high_dam_mask, "rtm_roll_volat"]

    u_stat, p_val_mwu = stats.mannwhitneyu(volat_high_dam, volat_norm_dam, alternative="greater")
    volat_ratio = volat_high_dam.mean() / max(1.0, volat_norm_dam.mean())
    logger.info(f"  -> RTM Volatility Ratio (High DAM vs Normal DAM): {volat_ratio:.2f}x (p-value: {p_val_mwu:.4e})")

    # -----------------------------------------------------------------------
    # Hypothesis 3: Time-of-Day & Diurnal Ramp Stratification
    # -----------------------------------------------------------------------
    logger.info("Testing Hypothesis 3: Diurnal Ramping & Stress Concentration...")
    def get_regime(b):
        if b <= 24:
            return "1. Night (00:00-06:00)"
        elif b <= 40:
            return "2. Morning Peak (06:00-10:00)"
        elif b <= 64:
            return "3. Solar Valley (10:00-16:00)"
        elif b <= 84:
            return "4. Evening Ramp (16:00-21:00)"
        else:
            return "5. Late Night (21:00-24:00)"

    df["regime"] = df["block_no"].apply(get_regime)
    regime_breakdown = df.groupby("regime").agg(
        avg_dam_imbalance=("dam_imbalance_ratio", "mean"),
        avg_spread=("dam_rtm_spread", "mean"),
        spike_rate=("rtm_spike", lambda x: np.mean(x) * 100.0),
    ).reset_index()

    evening_mask = df["block_no"].between(68, 82)
    pct_spikes_in_evening = (df.loc[evening_mask, "rtm_spike"].sum() / df["rtm_spike"].sum()) * 100.0
    logger.info(f"  -> % of All RTM Spikes in Evening Ramp Window: {pct_spikes_in_evening:.1f}%")

    # -----------------------------------------------------------------------
    # Hypothesis 4: Multi-Horizon Predictive Classification (1h, 2h, 4h)
    # -----------------------------------------------------------------------
    logger.info("Testing Hypothesis 4: Multi-Horizon Predictability with Zero Leakage...")
    horizons = {"1-Hour (h=1)": 4, "2-Hours (h=2)": 8, "4-Hours (h=4)": 16}
    horizon_results = []
    models_dict = {}

    split_idx = int(len(df) * 0.70)

    for h_name, lag in horizons.items():
        df_feat = build_features(df, horizon_blocks=lag)
        feature_cols = get_feature_columns(horizon_blocks=lag)

        # Drop NaN warmups
        valid = df_feat.dropna(subset=feature_cols + ["rtm_spike"]).reset_index(drop=True)

        train_data = valid.iloc[:split_idx]
        test_data = valid.iloc[split_idx:]

        X_tr, y_tr = train_data[feature_cols], train_data["rtm_spike"]
        X_te, y_te = test_data[feature_cols], test_data["rtm_spike"]

        clf = GradientBoostingClassifier(n_estimators=100, max_depth=4, random_state=42)
        clf.fit(X_tr, y_tr)
        models_dict[h_name] = (clf, feature_cols)

        probs = clf.predict_proba(X_te)[:, 1]
        preds = (probs >= 0.35).astype(int)

        auc = roc_auc_score(y_te, probs)
        brier = brier_score_loss(y_te, probs)
        prec = precision_score(y_te, preds, zero_division=0)
        rec = recall_score(y_te, preds, zero_division=0)

        horizon_results.append({
            "horizon": h_name,
            "lead_blocks": lag,
            "auc": round(auc, 3),
            "brier": round(brier, 3),
            "precision": round(prec, 3),
            "recall": round(rec, 3),
        })

    eval_df = pd.DataFrame(horizon_results)
    logger.info("\n" + eval_df.to_string(index=False))

    # -----------------------------------------------------------------------
    # Generate Publication Figures
    # -----------------------------------------------------------------------
    logger.info(f"Generating diagnostic charts in {output_dir}...")

    # Fig 1: Odds Ratio / Spike Rate by Regime
    plt.figure(figsize=(9, 5))
    bars = plt.bar(regime_breakdown["regime"], regime_breakdown["spike_rate"], color="#ef4444", width=0.55)
    plt.title("RTM Price Spike Occurrence Rate Across Grid Operating Regimes", fontsize=11, fontweight="bold")
    plt.ylabel("Spike Rate (% of blocks)", fontsize=10)
    plt.xticks(rotation=20, ha="right", fontsize=9)
    plt.grid(True, linestyle=":", alpha=0.5, axis="y")
    for bar in bars:
        h = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., h + 0.5, f"{h:.1f}%", ha="center", fontsize=9, fontweight="bold")
    plt.tight_layout()
    plt.savefig(output_dir / "fig1_spike_rate_by_regime.png", dpi=200)
    plt.close()

    # Fig 2: Multi-Horizon AUC Decay
    plt.figure(figsize=(7, 4.5))
    bars = plt.bar(eval_df["horizon"], eval_df["auc"], color=["#10b981", "#3b82f6", "#8b5cf6"], width=0.45)
    plt.axhline(0.5, color="gray", linestyle=":", label="Random Guess (0.50)")
    plt.ylim(0.5, 1.0)
    plt.title("Out-of-Sample ROC-AUC across Lead Horizons (Strict Zero Leakage)", fontsize=11, fontweight="bold")
    plt.ylabel("ROC-AUC Score", fontsize=10)
    for bar in bars:
        h = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., h + 0.015, f"{h:.3f}", ha="center", fontsize=9, fontweight="bold")
    plt.grid(True, linestyle=":", alpha=0.5, axis="y")
    plt.tight_layout()
    plt.savefig(output_dir / "fig2_multi_horizon_auc_decay.png", dpi=200)
    plt.close()

    # Fig 3: Feature Importance at 4h Horizon (DAM Signal Retention)
    clf_4h, f_4h = models_dict["4-Hours (h=4)"]
    imp_s = pd.Series(clf_4h.feature_importances_, index=f_4h).sort_values(ascending=True)
    plt.figure(figsize=(8, 5))
    imp_s.tail(8).plot(kind="barh", color="#2563eb", width=0.6)
    plt.title("Key Predictors at 4-Hour Horizon (DAM Fundamental Signal Dominance)", fontsize=11, fontweight="bold")
    plt.xlabel("Normalized Feature Importance", fontsize=10)
    plt.grid(True, linestyle=":", alpha=0.5)
    plt.tight_layout()
    plt.savefig(output_dir / "fig3_feature_importance_4h.png", dpi=200)
    plt.close()

    logger.info("✅ Phase 0 Feasibility Study completed successfully!")
    return {
        "odds_ratio": odds_ratio,
        "fisher_p_val": p_val_fisher,
        "evening_spike_pct": pct_spikes_in_evening,
        "auc_1h": eval_df.loc[eval_df["horizon"] == "1-Hour (h=1)", "auc"].values[0],
        "auc_4h": eval_df.loc[eval_df["horizon"] == "4-Hours (h=4)", "auc"].values[0],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Phase 0 Feasibility Study")
    parser.add_argument("--data-path", type=str, default=None, help="Path to unified market dataset CSV")
    parser.add_argument("--output-dir", type=str, default=None, help="Directory to save figures")
    args = parser.parse_args()

    run_phase0_study(data_path=args.data_path, output_dir=args.output_dir)
