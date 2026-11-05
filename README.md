# Multi-Horizon Probabilistic Framework for Indian Electricity Market Intelligence

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests: 20 Passed](https://img.shields.io/badge/tests-20%20passed-brightgreen.svg)](tests/)

> **Research Question**: Can the integration of high-frequency market bidding, trading and physical electricity-system indicators improve the prediction of market stress and price uncertainty in India's electricity market across intraday and day-ahead horizons?

---

## 1. Overview & Architecture

This repository implements an end-to-end econometric and machine learning framework to investigate whether **Day-Ahead Market (DAM) bidding behavior and physical power system indicators contain early-warning signals for subsequent Real-Time Market (RTM) price stress and volatility** on the Indian Energy Exchange (IEX).

```
┌────────────────────────────────────────────────────────────────────────┐
│                        REAL DATA INGESTION LAYER                       │
│  IEX DAM Historical     │  IEX DAM Snapshot  │  IEX RTM Snapshot       │
│  (233,760 blocks)       │  (Oct-Nov 2026)    │  (Oct-Nov 2026)         │
│  2018–2024              │  2,976 blocks      │  2,916 blocks           │
│                                              │                         │
│  Grid-India SCADA Generation Telemetry (29 monthly Excel files)       │
│  All-India Demand, Solar PV, Wind, Thermal, Hydro (5-min → 15-min)     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   POINT-IN-TIME FEATURE PIPELINE                       │
│  • DAM Imbalance Ratio: Purchase Bid / Sell Bid                        │
│  • Unsatisfied Demand: max(0, Purchase - MCV)                          │
│  • Spare Cushion: max(0, Sell - MCV)                                   │
│  • Net Demand: Physical Load - (Solar + Wind)                          │
│  • Evening Ramp Rate: ΔNet Demand (Blocks 68-82)                       │
│  • Lagged RTM Dynamics: Realized Volatility & Momentum (Zero Leakage)   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                     PROBABILISTIC RISK ENGINE                          │
│  • LightGBM Quantile Ensembles (P10, P25, P50, P75, P90, P99)          │
│  • Calibrated Spike Classifiers (Isotonic / Platt Scaling)             │
│  • Split Conformal Prediction (Finite-sample coverage guarantees)      │
│  • Multi-Horizon Alignment: 1h (h=1), 2h (h=2), 4h (h=4), Day-Ahead    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   STAKEHOLDER-ORIENTED RISK TRANSLATION                │
│  ┌──────────────────────┐ ┌──────────────────────┐ ┌─────────────────┐ │
│  │     Market View      │ │      Grid View       │ │Procurement View │ │
│  │ VaR 95%, Tail ES 95% │ │ Supply-Demand Tension│ │ DAM-RTM Spread  │ │
│  │ Regime: CALM/VOLATILE│ │ Net Ramp Alert (MW)  │ │ Arbitrage Hedge │ │
│  │ Spike Probabilities  │ │ Liquidity Drought    │ │ Exposure (Lakhs)│ │
│  └──────────────────────┘ └──────────────────────┘ └─────────────────┘ │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 🎓 Academic Core Submission: Applied Probability Distributions (THM6242)

This repository serves a dual role: it contains our complete **Production-Grade Automated Capstone Platform** and hosts the dedicated **Theoretical Probability Foundation** developed for academic assessment at **Symbiosis Statistical Institute (SSI), Symbiosis International (Deemed University)** for Course **Applied Probability Distributions (THM6242)** under the mentorship of **Dr. Monika Vishnoi**.

All academic deliverables are neatly packaged in [`academic_submission/`](academic_submission/):

| Academic Deliverable | File Path | Format & Extent | Key Curriculum Requirements Fulfilled |
| :--- | :--- | :--- | :--- |
| **Comprehensive Academic Project Report** | [`academic_submission/reports/Group05_Title05_Report.docx`](academic_submission/reports/Group05_Title05_Report.docx)<br>[`Group05_Title05_Report.pdf`](academic_submission/reports/Group05_Title05_Report.pdf) | Word (.docx) & PDF (A4, 12pt, 1.5 spacing, 22–25 pages) | Covers Units 1–5, formal proofs, step-by-step hand calculation, 9 tables, 6 figures, real-world grid interpretations. |
| **Practical Jupyter Notebook** | [`notebooks/SSI_THM6242_Applied_Probability_Project.ipynb`](notebooks/SSI_THM6242_Applied_Probability_Project.ipynb) | Executed `.ipynb` (Local & Google Colab compatible) | From-scratch NumPy algorithms cross-verified against `scipy.stats`; runs top-to-bottom with pre-rendered outputs. |
| **Presentation Slide Deck** | [`academic_submission/presentation/Group05_Title05_Presentation.pptx`](academic_submission/presentation/Group05_Title05_Presentation.pptx) | PowerPoint (15 Widescreen Slides) | Follows exact SSI Section 5 presentation order for a 10-minute presentation and viva. |
| **Viva Defense & Theory Guide** | [`academic_submission/viva_prep/VIVA_PREPARATION_AND_DEFENSE_GUIDE.md`](academic_submission/viva_prep/VIVA_PREPARATION_AND_DEFENSE_GUIDE.md) | Markdown Reference | Comprehensive Q&A cheat sheet addressing anticipated examiner questions on parameter choices, code lines, $\chi^2$ values, and Units 1–4 fundamentals. |
| **Student Declaration Sheet** | [`academic_submission/declaration/Student_Declaration_and_Contribution_Sheet.docx`](academic_submission/declaration/Student_Declaration_and_Contribution_Sheet.docx) | Word (.docx) | Formal academic integrity declaration and team task responsibility matrix. |
| **Data Provenance & Citations** | [`academic_submission/data_citation/DATA_CITATIONS_AND_SOURCES.md`](academic_submission/data_citation/DATA_CITATIONS_AND_SOURCES.md) | Markdown Reference | Full academic citations and download links for IEX, CERC, and Grid-India datasets. |

### Summary of Theoretical Probability Findings:
1. **Unit 1 (Expectation & Conditional Expectation):** Day-Ahead market imbalance explains **49.10% of total real-time price variance** via the Law of Total Variance. Conditional mean jumps from ₹1,837 to ₹7,408/MWh (**4.03x surge**).
2. **Unit 2 (Discrete Spike Modeling):** Daily spike counts exhibit severe overdispersion ($\text{Var}/\text{Mean} = 20.51$). Poisson fails; Negative Binomial ($\hat{r} = 1.795, \hat{p} = 0.0488$) captures transmission and generator outage clustering.
3. **Unit 2 (Continuous Densities):** Positive clearing prices fit Two-Parameter Gamma ($\hat{\alpha} = 1.9144, \hat{\theta} = 2952.85$) and Weibull ($\hat{c} = 1.5831, \hat{\lambda} = 6272.61$) densities, derived from scratch and verified with `scipy.stats`.
4. **Unit 3 (Sampling Distributions):** Welch's $t$-test confirms Evening Ramp prices are decisively higher than Mid-day Solar ($t = 46.80, p < 10^{-200}$) and 5.80x more volatile ($F = 5.80, p < 10^{-15}$). $\chi^2 = 6,943.23$ demonstrates that 88.37% of divergence is driven by CERC's ₹10,000 regulatory price ceiling.
5. **Unit 4 (Order Statistics & CLT):** Intra-day maximum order statistic $X_{(96)}$ hits the ₹10,000 ceiling in **90.32% of trading days**. Aggregated procurement sums converge to Gaussianity (kurtosis drops from $-1.571$ to $+0.094$), validating classical portfolio VaR budgeting under the Central Limit Theorem.

---

## 2. Dataset Inventory & Exact Features Processed

All raw datasets are located in `data/raw/` and processed via `src/data_pipeline/`:

### A. Real Datasets Present in `data/raw/`

| File / Folder | Resolution | Date Span | Size / Rows | Role in Framework |
| :--- | :--- | :--- | :--- | :--- |
| `data/raw/DAM.xlsx` & `DAM.csv` | 15-min (96 blocks/day) | Jan 2018 – Aug 2024 | **233,760 blocks** (~25 MB) | Multi-year historical day-ahead bidding and clearance |
| `data/raw/DAM_Market Snapshot.xlsx` | 15-min | Oct 03, 2026 – Nov 02, 2026 | **2,976 blocks** (~233 KB) | Official IEX Day-Ahead auction snapshot |
| `data/raw/RTM_Market Snapshot.xlsx` | 15-min (48 sessions) | Oct 03, 2026 – Nov 02, 2026 | **2,916 blocks** (~241 KB) | Official IEX Real-Time auction snapshot (synchronized) |
| `data/raw/Electricity Demand, Solar and Wind Generation Data/` | 5-min SCADA | Sept 2021 – June 2025 | **29 monthly files** (~670 MB) | Grid-India physical demand & renewable generation telemetry |

---

### B. What Features Are Processed and How

#### 1. Market Clearing & Bidding Signals (`iex_loader.py` & `feature_engine.py`)
- **`purchase_bid_mw`**: Aggregate demand bids submitted by Discoms and industrial buyers.
- **`sell_bid_mw`**: Aggregate supply bids submitted by power generators and sellers.
- **`mcv_mw`**: Market Clearing Volume (quantum matched and cleared by the double-sided auction).
- **`dam_mcp` / `rtm_mcp`**: Uniform clearing prices (₹/MWh), strictly bounded by CERC price caps (₹0 to ₹10,000/MWh).
- **`dam_imbalance_ratio = purchase_bid_mw / max(sell_bid_mw, 1.0)`**:
  - *Processing*: Key structural metric of market tightness. When $> 1.0$, buying interest exceeds available supply.
- **`dam_unsatisfied_demand_mw = max(0, purchase_bid_mw - mcv_mw)`**:
  - *Processing*: Measures unfulfilled demand forced into the Real-Time Market or bilateral balancing.
- **`dam_supply_cushion_mw = max(0, sell_bid_mw - mcv_mw)`**:
  - *Processing*: Spare merchant generation capacity available on the exchange.
- **`dam_rtm_spread = rtm_mcp - dam_mcp`**:
  - *Processing*: Real-time price spread. Positive values indicate real-time scarcity premium.

#### 2. Point-in-Time Lagged RTM Dynamics (Strict Zero-Leakage)
- For target block $b$, the bidding gate closes strictly 1 hour prior to physical delivery ($T - 1.0\text{h}$).
- **`rtm_mcp_lag_{h}`**: Lagged RTM clearing price at lead horizon $h$ ($h=4$ blocks for 1h, $h=8$ for 2h, $h=16$ for 4h).
- **`rtm_spread_lag_{h}`**: Realized DAM-RTM spread shifted by $h$ blocks.
- **`rtm_volat_lag_{h}`**: 8-block rolling standard deviation of RTM prices, shifted by $h$ blocks.
- **`rtm_momentum_lag_{h}`**: Price velocity over the preceding 4 blocks ($\Delta \text{MCP}_{RTM}$).

#### 3. Grid-India Physical SCADA Telemetry (`Electricity Demand, Solar and Wind Generation Data/`)
- **`grid_demand_mw`** (`NLDC_DEMAND`): Total All-India instantaneous electrical load.
- **`solar_generation_mw`** (`ALL_IND_SOLAR`): Total national solar PV generation.
- **`wind_generation_mw`** (`ALL_INDIA_WIND`): Total national wind power injection.
- **`net_demand_mw = grid_demand_mw - (solar_generation_mw + wind_generation_mw)`**:
  - *Processing*: Computes the actual "Duck Curve" residual load that conventional thermal and hydro generators must follow.
- **`net_demand_ramp_15min = net_demand(t) - net_demand(t-1)`**:
  - *Processing*: Rate of ramp pressure (MW/15-min). Identifies extreme stress during evening solar drop-off.
- **`solar_share_pct`** & **`renewable_share_pct`**: Instantaneous renewable penetration ratios.

#### 4. Diurnal & Calendar Encodings
- **`sin_block`** & **`cos_block`**: Circular harmonic encodings for the 96 diurnal settlement blocks ($\sin(2\pi b / 96)$).
- **`is_evening_ramp`**: Binary indicator for blocks 68–82 (17:00–20:30 IST), when solar PV collapses while lighting load surges.
- **`is_morning_ramp`**: Binary indicator for blocks 28–38 (07:00–09:30 IST).
- **`day_of_week`**, **`is_weekend`**, **`month`**.

---

## 3. Empirical Phase 0 Feasibility Findings on Real Data

Running `python -m studies.phase0_feasibility.run_feasibility` on the synchronized real IEX data yields the following empirical validation:

```text
======================================================================
PHASE 0 EMPIRICAL RESULTS (Real IEX DAM–RTM Dataset: 2,916 Blocks)
======================================================================
1. Hypothesis 1 (Tightness Propagation):
   • Odds Ratio: 44.23× (p-value: 5.77e-288)
   • Point-Biserial Correlation: 0.661
   >> CONCLUSION: High DAM purchase-to-sell ratio overwhelmingly precedes RTM spikes.

2. Hypothesis 3 (Diurnal Ramping Concentration):
   • 32.3% of all extreme price spikes occur in the Evening Ramp window (Blocks 68-82).

3. Hypothesis 4 (Multi-Horizon Predictability with Zero Leakage):
   • 1-Hour Ahead (h=1):  ROC-AUC = 0.981 | Brier = 0.027 | Precision = 0.729 | Recall = 0.773
   • 2-Hours Ahead (h=2): ROC-AUC = 0.978 | Brier = 0.023 | Precision = 0.833 | Recall = 0.758
   • 4-Hours Ahead (h=4): ROC-AUC = 0.965 | Brier = 0.031 | Precision = 0.843 | Recall = 0.652
======================================================================
```

---

## 4. How to Run the Pipeline & Models

### Step 1: Process All Datasets
Process raw snapshots, resample SCADA telemetry, and generate engineered feature tables:
```bash
python -m src.data_pipeline.process_all_datasets
```
Outputs generated in `data/processed/`:
- `real_dam_rtm_synchronized.csv` (2,916 real 15-min blocks with all engineered features)
- `grid_scada_resampled_15min.csv` (11,712 resampled 15-min SCADA blocks)
- `dam_historical_2018_2024.csv` (233,760 cleaned historical DAM blocks)
- `dataset_summary.json` (Full summary metadata)

### Step 2: Run the Feasibility Study & Generate Publication Charts
```bash
python -m studies.phase0_feasibility.run_feasibility --data-path data/processed/real_dam_rtm_synchronized.csv
```
Diagnostic figures are automatically saved to `studies/phase0_feasibility/figures/`:
- `fig1_spike_rate_by_regime.png`
- `fig2_multi_horizon_auc_decay.png`
- `fig3_feature_importance_4h.png`

### Step 3: Run the Full Test Suite
```bash
pytest tests/ -v
# 20 passed in 2.4s (100% test pass rate)
```

### Step 4: Launch the Interactive Dashboard Prototype
```bash
uvicorn src.dashboard.app:app --reload --port 8000
```
Open `http://localhost:8000` to interact with:
- **Market Tab**: 96-block fan charts ($P_{10}$ to $P_{99}$), VaR 95%, Expected Shortfall, and regime badges.
- **Grid Tab**: Real-time supply-demand pressure gauge and net demand ramp warnings.
- **Procurement Tab**: DAM vs RTM spread forecast, cost-optimal hedging recommendations, and financial exposure calculator.

---

## 5. Repository File Structure

```
indian_power_market/
├── data/
│   ├── raw/
│   │   ├── DAM.csv                               # 15-min DAM series (233k blocks)
│   │   ├── DAM.xlsx                              # Multi-year historical DAM
│   │   ├── DAM_Market Snapshot.xlsx              # IEX official DAM snapshot
│   │   ├── RTM_Market Snapshot.xlsx              # IEX official RTM snapshot
│   │   └── Electricity Demand, Solar and Wind... # 29 SCADA monthly Excel files
│   └── processed/
│       ├── real_dam_rtm_synchronized.csv         # Featured synchronized dataset
│       ├── grid_scada_resampled_15min.csv        # Resampled 15-min SCADA series
│       ├── dam_historical_2018_2024.csv          # 233k cleaned historical blocks
│       └── dataset_summary.json                  # Metadata and summary statistics
├── src/
│   ├── data_pipeline/
│   │   ├── iex_schema.py                         # 96 blocks, 48 sessions, CERC caps
│   │   ├── iex_loader.py                         # Loaders for snapshot, historical & SCADA
│   │   ├── synthetic_generator.py                # Calibrated benchmark generator
│   │   ├── feature_engine.py                     # Zero-leakage temporal feature extraction
│   │   └── process_all_datasets.py               # Automated pipeline runner
│   ├── risk_engine/
│   │   ├── horizons.py                           # 1h, 2h, 4h, and D+1 alignment
│   │   ├── quantile_models.py                    # LightGBM Quantile Regression + CRPS
│   │   ├── stress_classifier.py                  # Calibrated Classifier (Isotonic / Platt)
│   │   ├── conformal.py                          # Split Conformal Prediction
│   │   └── explainability.py                     # SHAP & DAM vs. RTM signal retention
│   ├── stakeholders/
│   │   ├── market_view.py                        # Market Risk Index, VaR 95%, ES 95%
│   │   ├── grid_view.py                          # Supply-Demand Pressure Index & Ramp Alerts
│   │   └── procurement_view.py                   # DAM-RTM Spread Arbitrage & Exposure Math
│   └── dashboard/
│       ├── app.py                                # FastAPI backend
│       └── templates/index.html                  # Interactive Tailwind + Plotly UI
├── studies/
│   └── phase0_feasibility/
│       ├── run_feasibility.py                    # Standalone hypothesis test runner
│       └── figures/                              # Generated publication charts
├── notebooks/
│   ├── 01_Data_Loading_and_Preparation.ipynb     # Colab multi-source ingestion
│   └── 02_Phase0_Feasibility_Study.ipynb         # Colab Phase 0 empirical tests
├── tests/
│   ├── test_data_pipeline.py                     # Schema, 96 blocks/day, zero leakage
│   ├── test_risk_engine.py                       # Quantile monotonicity, calibration
│   └── test_stakeholders.py                      # Risk indexes, alert thresholds
├── pyproject.toml
├── requirements.txt
└── README.md
```

## License

MIT License. See [LICENSE](LICENSE) for details.
