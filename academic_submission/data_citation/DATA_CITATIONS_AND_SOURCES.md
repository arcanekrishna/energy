# Data Citations, Sources and Provenance
## Symbiosis Statistical Institute [SSI] | Course THM6242: Applied Probability Distributions

This document provides formal academic citations, data repository URLs, and provenance records for all datasets utilized in the project:
**"Empirical Characterization and Probabilistic Modeling of Price Formation, Extreme Volatility, and Daily Spike Dynamics in the Indian Electricity Market (IEX)"**

---

### 1. Primary Operational Market Datasets
* **Data Source:** Indian Energy Exchange Limited (IEX), New Delhi, India.
* **Datasets Utilized:**
  1. `DAM_Market Snapshot.xlsx`: Double-sided auction bidding volumes and uniform Market Clearing Prices (MCP) for the Day-Ahead Market across 96 fifteen-minute operational blocks per trading day.
  2. `RTM_Market Snapshot.xlsx`: Half-hourly continuous balancing market clearing prices and purchase/sell bid volumes for the Real-Time Market across 48 operational half-hour windows (96 dispatch intervals) per day.
  3. `DAM.xlsx` & `DAM.csv`: Historical multi-year Day-Ahead Market clearing data spanning 2018 to 2024 (233,760 fifteen-minute observations).
* **Sample Period for Empirical Analysis:** October 3, 2026 to November 2, 2026 (2,916 synchronized 15-minute dispatch blocks, 31 trading days).
* **Official Portal URL:** [https://www.iexindia.com/marketdata/market_snapshot.aspx](https://www.iexindia.com/marketdata/market_snapshot.aspx)
* **Citation:**  
  Indian Energy Exchange (IEX). (2026). *Day-Ahead Market (DAM) and Real-Time Market (RTM) Operational Snapshot Data*. New Delhi: IEX India.

---

### 2. Physical Grid Telemetry and Generation Data
* **Data Source:** Grid Controller of India Limited (Grid-India, formerly POSOCO) / National Load Despatch Centre (NLDC).
* **Dataset Utilized:** `Electricity Demand, Solar and Wind Generation Data/` (29 monthly telemetry workbooks).
* **Variables Extracted:** 5-minute SCADA telemetry of All-India electricity demand met (MW), solar photovoltaic generation (MW), wind turbine generation (MW), net demand (MW), and 15-minute intra-day ramp rates (MW/block).
* **Official Portal URL:** [https://grid-india.in/reports/operational-reports/](https://grid-india.in/reports/operational-reports/)
* **Citation:**  
  Grid Controller of India Limited (Grid-India). (2024–2026). *National Load Despatch Centre (NLDC) Operational Performance & Renewable Telemetry Reports*. Ministry of Power, Government of India.

---

### 3. Regulatory Orders & Statutory Price Ceiling Mandates
* **Regulatory Authority:** Central Electricity Regulatory Commission (CERC), New Delhi, India.
* **Regulatory Instrument:** Order in Suo-Motu Petition No. 04/SM/2022 (Extended under subsequent orders).
* **Statutory Requirement:** Mandated price ceiling of ₹10,000/MWh (₹10/kWh) across all spot physical market segments (DAM, RTM, Intra-Day, Term-Ahead) on Indian power exchanges to mitigate runaway market power during transmission bottlenecks and peak evening ramps.
* **Official Portal URL:** [https://cercind.gov.in/orders.html](https://cercind.gov.in/orders.html)
* **Citation:**  
  Central Electricity Regulatory Commission (CERC). (2022). *Order on Review of Ceiling Price in Power Exchanges (Petition No. 4/SM/2022)*. New Delhi: Government of India.

---

### 4. Processed Data Repository and Open-Source Code Access
* **GitHub Repository:** [https://github.com/arcanekrishna/energy](https://github.com/arcanekrishna/energy)
* **Branch:** `main`
* **Direct Raw CSV Download Link (for Google Colab execution):**  
  `https://raw.githubusercontent.com/arcanekrishna/energy/main/data/processed/real_dam_rtm_synchronized.csv`
* **Directory Structure in Repository:**
  ```text
  data/
  ├── raw/
  │   ├── DAM_Market Snapshot.xlsx
  │   ├── RTM_Market Snapshot.xlsx
  │   ├── DAM.xlsx
  │   └── Electricity Demand, Solar and Wind Generation Data/
  └── processed/
      ├── real_dam_rtm_synchronized.csv   (2,916 blocks)
      ├── grid_scada_resampled_15min.csv   (11,712 blocks)
      └── dam_historical_2018_2024.csv    (233,760 blocks)
  ```
