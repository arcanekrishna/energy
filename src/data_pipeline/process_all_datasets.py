"""
End-to-End Real Dataset Processor for Indian Electricity Market Intelligence.

Processes raw IEX snapshots, multi-year historical records, and Grid-India SCADA telemetry:
1. Merges DAM and RTM Market Snapshots (2026 synchronous delivery blocks).
2. Resamples and processes SCADA generation data (Demand, Solar, Wind, Hydro, Thermal).
3. Cleans and standardizes multi-year historical DAM (2018-2024, 230k+ blocks).
4. Generates point-in-time engineered features with zero look-ahead bias.
5. Saves processed files to data/processed/ with metadata summaries.
"""

from __future__ import annotations

import json
import logging
import os
import sys
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import numpy as np
import pandas as pd

from src.data_pipeline.feature_engine import build_features
from src.data_pipeline.iex_loader import (
    load_dam_historical_xlsx,
    load_market_snapshot,
    load_scada_renewables_timeseries,
    merge_real_dam_rtm_snapshots,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("process_datasets")


def process_all():
    raw_dir = ROOT_DIR / "data" / "raw"
    processed_dir = ROOT_DIR / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)

    summary = {}

    # -----------------------------------------------------------------------
    # 1. Process Synchronized DAM & RTM Market Snapshots
    # -----------------------------------------------------------------------
    dam_snap_path = raw_dir / "DAM_Market Snapshot.xlsx"
    rtm_snap_path = raw_dir / "RTM_Market Snapshot.xlsx"

    if dam_snap_path.exists() and rtm_snap_path.exists():
        logger.info("--- Step 1: Processing Synchronized DAM and RTM Snapshots ---")
        merged_snap = merge_real_dam_rtm_snapshots(dam_snap_path, rtm_snap_path)

        # Build multi-horizon features (e.g. 1h = 4 blocks lead)
        featured_snap = build_features(merged_snap, horizon_blocks=4)

        out_snap_path = processed_dir / "real_dam_rtm_synchronized.csv"
        featured_snap.to_csv(out_snap_path, index=False)
        logger.info("Saved %d featured snapshot blocks to %s", len(featured_snap), out_snap_path)

        summary["synchronized_snapshots"] = {
            "total_blocks": len(featured_snap),
            "start_date": str(featured_snap["date"].min()),
            "end_date": str(featured_snap["date"].max()),
            "dam_mcp_mean_rs_mwh": float(featured_snap["dam_mcp"].mean()),
            "rtm_mcp_mean_rs_mwh": float(featured_snap["rtm_mcp"].mean()),
            "mean_spread_rs_mwh": float(featured_snap["dam_rtm_spread"].mean()),
            "spike_rate_pct": float(featured_snap["rtm_spike"].mean() * 100.0),
        }

    # -----------------------------------------------------------------------
    # 2. Process SCADA Telemetry (Demand, Solar, Wind, Thermal, Hydro)
    # -----------------------------------------------------------------------
    scada_dir = raw_dir / "Electricity Demand, Solar and Wind Generation Data"
    if scada_dir.exists():
        logger.info("--- Step 2: Processing SCADA Generation & Demand Telemetry ---")
        # Process sample of files (e.g., 3 months to avoid long processing time during rapid verification)
        df_scada = load_scada_renewables_timeseries(scada_dir, max_files=4)
        if not df_scada.empty:
            out_scada_path = processed_dir / "grid_scada_resampled_15min.csv"
            df_scada.to_csv(out_scada_path, index=False)
            logger.info("Saved %d resampled 15-min SCADA blocks to %s", len(df_scada), out_scada_path)

            summary["scada_telemetry"] = {
                "total_15min_blocks": len(df_scada),
                "start_date": str(df_scada["date"].min()),
                "end_date": str(df_scada["date"].max()),
                "mean_demand_mw": float(df_scada["grid_demand_mw"].mean()),
                "max_solar_mw": float(df_scada["solar_generation_mw"].max()),
                "mean_net_demand_mw": float(df_scada["net_demand_mw"].mean()),
                "max_evening_ramp_mw_15min": float(df_scada["net_demand_ramp_15min"].max()),
            }

    # -----------------------------------------------------------------------
    # 3. Process Multi-Year Historical DAM (DAM.xlsx)
    # -----------------------------------------------------------------------
    dam_hist_path = raw_dir / "DAM.xlsx"
    if dam_hist_path.exists():
        logger.info("--- Step 3: Processing Historical DAM (230k+ blocks) ---")
        df_dam_hist = load_dam_historical_xlsx(dam_hist_path)
        out_hist_path = processed_dir / "dam_historical_2018_2024.csv"
        df_dam_hist.to_csv(out_hist_path, index=False)
        logger.info("Saved %d historical DAM blocks to %s", len(df_dam_hist), out_hist_path)

        summary["historical_dam"] = {
            "total_blocks": len(df_dam_hist),
            "start_date": str(df_dam_hist["date"].min()),
            "end_date": str(df_dam_hist["date"].max()),
            "mean_dam_mcp_rs_mwh": float(df_dam_hist["dam_mcp"].mean()),
            "p90_dam_mcp_rs_mwh": float(df_dam_hist["dam_mcp"].quantile(0.90)),
        }

    # Write summary metadata
    with open(processed_dir / "dataset_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    logger.info("✅ All datasets successfully processed! Summary saved to %s", processed_dir / "dataset_summary.json")
    print("\n" + json.dumps(summary, indent=2))


if __name__ == "__main__":
    process_all()
