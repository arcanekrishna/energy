# Multi-Horizon Probabilistic Framework for Indian Electricity Market Intelligence

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **Research Question**: Can the integration of high-frequency market bidding, trading and physical electricity-system indicators improve the prediction of market stress and price uncertainty in India's electricity market across intraday and day-ahead horizons?

## Overview

This project investigates whether **Day-Ahead Market (DAM) bidding behavior contains early-warning signals for subsequent stress and extreme price events in the Real-Time Market (RTM)** on the Indian Energy Exchange (IEX).

It provides:
- **Multi-horizon probabilistic forecasts** (1h, 2h, 4h ahead, day-ahead) for electricity prices
- **Calibrated spike probability estimates** for market stress events
- **Three stakeholder-specific risk dashboards**: Market operators, Grid operators, and Procurement managers
- **Rigorous zero-leakage temporal architecture** preventing look-ahead bias

```
┌─────────────────────────────────────────────────────────────────┐
│                    DATA LAYER                                   │
│  IEX DAM (Real)  │  IEX RTM  │  Demand+Solar+Wind  │  Weather  │
└────────┬──────────┴─────┬─────┴──────────┬──────────┴─────┬─────┘
         │                │                │                │
         ▼                ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│              ZERO-LEAKAGE FEATURE ENGINE                        │
│  DAM imbalance ratio │ Lagged RTM │ Solar ramp │ Cyclical time  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                 RISK ENGINE                                     │
│  LightGBM Quantile │ Calibrated Classifier │ Conformal Pred.   │
└──────┬──────────────┴──────────┬────────────┴──────┬────────────┘
       │                        │                    │
       ▼                        ▼                    ▼
┌──────────────┐  ┌──────────────────┐  ┌────────────────────────┐
│ Market View  │  │   Grid View      │  │  Procurement View      │
│ VaR, spikes  │  │ Ramp warnings    │  │ DAM-RTM spread,        │
│ regime class │  │ liquidity alerts  │  │ strategy recommender   │
└──────────────┘  └──────────────────┘  └────────────────────────┘
```

## Key Research Hypotheses

1. **DAM Tightness → RTM Spikes**: High DAM purchase-to-sell ratio precedes RTM price spikes
2. **Spread Persistence**: Extreme DAM clearance prices predict elevated real-time volatility
3. **Diurnal Concentration**: Evening solar ramp (blocks 68–82, 17:00–20:30) amplifies stress propagation
4. **Multi-Horizon Retention**: DAM indicators maintain predictive power 1h, 2h, and 4h ahead

## Repository Structure

```
indian_power_market/
├── src/
│   ├── data_pipeline/          # Data ingestion, validation, feature engineering
│   │   ├── iex_schema.py       # IEX market structure & validation rules
│   │   ├── iex_loader.py       # Multi-source data loading & standardization
│   │   ├── synthetic_generator.py  # Calibrated synthetic RTM generator
│   │   └── feature_engine.py   # Zero-leakage temporal feature extraction
│   ├── risk_engine/            # Probabilistic forecasting models
│   │   ├── horizons.py         # Multi-horizon dataset alignment (1h/2h/4h/D+1)
│   │   ├── quantile_models.py  # LightGBM quantile regression (P10–P99)
│   │   ├── stress_classifier.py # Calibrated spike probability classifier
│   │   ├── conformal.py        # Conformal prediction intervals
│   │   └── explainability.py   # SHAP & feature importance analysis
│   ├── stakeholders/           # Stakeholder-specific risk translation
│   │   ├── market_view.py      # VaR, Expected Shortfall, regime classification
│   │   ├── grid_view.py        # Supply-demand pressure, ramp warnings
│   │   └── procurement_view.py # DAM-RTM spread arbitrage & strategy
│   └── dashboard/              # Interactive web dashboard
│       ├── app.py              # FastAPI backend
│       └── templates/          # HTML/JS frontend
├── studies/
│   └── phase0_feasibility/     # DAM→RTM early warning feasibility study
├── notebooks/                  # Google Colab notebooks
│   ├── 01_Data_Loading_and_Preparation.ipynb
│   └── 02_Phase0_Feasibility_Study.ipynb
├── tests/                      # Comprehensive test suite
├── data/
│   ├── raw/                    # Downloaded datasets (gitignored)
│   └── processed/              # Processed outputs (gitignored)
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Datasets

| # | Dataset | Source | Role |
|---|---------|--------|------|
| 1 | IEX DAM prices & volumes | [Kaggle](https://www.kaggle.com/datasets/mukund604/indian-energy-exchange-time-series-forecasting) | Core predictor |
| 2 | Hourly demand + solar + wind | [Mendeley DOI:10.17632/y58jknpgs8.2](https://doi.org/10.17632/y58jknpgs8.2) | Exogenous features |
| 3 | State demand + weather | [Zenodo DOI:10.5281/zenodo.14983362](https://doi.org/10.5281/zenodo.14983362) | Seasonal context |
| 4 | Calibrated synthetic RTM | Generated in-code | Target variable |

## Quick Start

### Installation

```bash
git clone https://github.com/YOUR_USERNAME/indian-power-market-intelligence.git
cd indian-power-market-intelligence
pip install -r requirements.txt
```

### Run Phase 0 Feasibility Study

```bash
# With synthetic data (no downloads needed)
python -m studies.phase0_feasibility.run_feasibility

# With real data (after downloading datasets)
python -m studies.phase0_feasibility.run_feasibility --data-dir data/processed/
```

### Run Tests

```bash
pytest tests/ -v
```

### Launch Dashboard

```bash
uvicorn src.dashboard.app:app --reload --port 8000
# Open http://localhost:8000
```

### Google Colab

Upload the notebooks from `notebooks/` to Google Colab and follow the step-by-step instructions.

## Algorithms & Methods

| Component | Method | Why |
|-----------|--------|-----|
| Price forecasting | LightGBM Quantile Regression | State-of-the-art for tabular EPF; outperforms deep learning on structured energy data |
| Spike classification | Gradient Boosting + Isotonic Calibration | Well-calibrated probabilities for decision-making |
| Prediction intervals | Conformal Prediction (Split) | Distribution-free coverage guarantees |
| Feature importance | SHAP TreeExplainer | Quantifies DAM vs RTM predictive contribution per horizon |
| Evaluation | CRPS, Brier Score, Pinball Loss, Coverage | Standard probabilistic forecast metrics |

## Domain Constants

| Parameter | Value |
|-----------|-------|
| Time blocks per day | 96 (15-minute intervals) |
| RTM sessions per day | 48 (each covers 2 blocks) |
| DAM gate closure | D-1, ~14:00 IST |
| RTM gate closure | T-delivery minus 1 hour |
| CERC price cap | ₹10,000/MWh (₹10/kWh) |
| Evening ramp stress window | Blocks 65–84 (16:00–21:00 IST) |

## License

MIT License. See [LICENSE](LICENSE) for details.

## Citation

If you use this work in your research, please cite:

```bibtex
@software{indian_power_market_intelligence,
  title={Multi-Horizon Probabilistic Framework for Indian Electricity Market Intelligence},
  year={2024},
  url={https://github.com/YOUR_USERNAME/indian-power-market-intelligence}
}
```
