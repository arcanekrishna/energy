# Symbiosis Statistical Institute [SSI] | Course THM6242 Academic Submission Package
## Applied Probability Distributions (Sem-I, Batch 2026-2028)
**Course Instructor:** Dr. Monika Vishnoi  
**Component III (Project Report & Practical Notebook - 30 Marks)**  
**Component IV (Presentation & Viva - 30 Marks)**  
**Project Title:** Empirical Characterization and Probabilistic Modeling of Price Formation, Extreme Volatility, and Daily Spike Dynamics in the Indian Electricity Market (IEX)  
**Associated GitHub Repository:** [https://github.com/arcanekrishna/energy](https://github.com/arcanekrishna/energy)

---

## 📁 Academic Package Directory Contents

```text
academic_submission/
├── reports/
│   ├── Group05_Title05_Report.docx         <-- Complete Academic Report (Word format, 12pt, 1.5 spacing, 22-25 pages)
│   └── Group05_Title05_Report.pdf          <-- Rendered Academic Report (PDF format, formal headers & page numbers)
├── notebooks/
│   └── SSI_THM6242_Applied_Probability_Project.ipynb  <-- Clean, fully executed Jupyter Notebook (Local & Colab compatible)
├── presentation/
│   └── Group05_Title05_Presentation.pptx   <-- 15-Slide Presentation Deck matching SSI Section 5 rubric
├── viva_prep/
│   └── VIVA_PREPARATION_AND_DEFENSE_GUIDE.md  <-- Comprehensive Viva Defense Cheat Sheet & question bank
├── declaration/
│   └── Student_Declaration_and_Contribution_Sheet.docx  <-- Signed declaration & task responsibility matrix
├── data_citation/
│   └── DATA_CITATIONS_AND_SOURCES.md       <-- Formal citations for IEX, Grid-India, CERC datasets & URLs
└── figures/
    ├── fig1_diurnal_price_duck_curve.png   <-- Figure 1: Diurnal price duck curve & evening surge
    ├── fig2_conditional_expectation_regimes.png <-- Figure 2: Boxplot across regimes & variance decomposition
    ├── fig3_discrete_spike_poisson_vs_negbinom.png <-- Figure 3: Poisson vs Negative Binomial overdispersion
    ├── fig4_continuous_price_gamma_weibull.png <-- Figure 4: Gamma vs Weibull densities & CERC cap truncation
    ├── fig5_order_statistics_daily_max.png <-- Figure 5: Order statistics X_(96) & cap saturation
    └── fig6_central_limit_theorem_convergence.png <-- Figure 6: Central Limit Theorem Monte Carlo convergence
```

---

## 🎯 Syllabus Mapping to Course Units

| Course Syllabus Unit | Theoretical Concept Applied | First-Principles NumPy Implementation | Empirical Result on Real IEX Data |
| :--- | :--- | :--- | :--- |
| **Unit 1: Expectation & Conditional Expectation** | Law of Iterated Expectations & Law of Total Variance | $\sum P(X=r)\mu_r$ and $\sum P(X=r)\sigma_r^2 + \sum P(X=r)(\mu_r - \mu)^2$ | **49.10% of total RTM price variance** is explained by Day-Ahead imbalance regimes. Expected price jumps from ₹1,837 to ₹7,408/MWh (**4.03x surge**). |
| **Unit 2: Discrete Distributions** | Poisson vs. Negative Binomial (Gamma-Poisson Mixture) | Method of Moments: $\hat{p} = \bar{k}/s^2, \hat{r} = \bar{k}^2/(s^2 - \bar{k})$ | **Severe Overdispersion** ($\text{Var}/\text{Mean} = 20.51$). Poisson fails; Negative Binomial accommodates physical generator outage clustering. |
| **Unit 2: Continuous Distributions** | Two-Parameter Gamma & Weibull Densities | Brent's root-scalar optimization of digamma equation $\ln \alpha - \psi(\alpha) = \ln \bar{x} - \overline{\ln x}$ | Gamma parameters $\hat{\alpha} = 1.9144, \hat{\theta} = 2952.85$; cross-verified with `scipy.stats` to $< 10^{-8}$ discrepancy. |
| **Unit 3: Sampling Distributions ($\chi^2, t, F$)** | Pearson $\chi^2$ Goodness-of-Fit, Welch's $t$-test, $F$-test | From-scratch binning, expected frequencies $E_j$, and test statistics | Evening ramp prices are significantly higher ($t = 46.80, p < 10^{-200}$) and 5.80x more volatile ($F = 5.80, p < 10^{-15}$). $\chi^2 = 6943.23$ reveals that 88.37% of divergence is caused by CERC ₹10,000 regulatory cap accumulation. |
| **Unit 4: Order Statistics & CLT** | Extreme Order Statistic $X_{(96)} = \max P_i$ & Lindeberg-Lévy CLT | Theoretical CDF $[F(x)]^{96}$ and Monte Carlo portfolio block bootstrap ($n=1, 4, 16, 96$) | Daily peak hits the ₹10,000 cap in **90.32% of trading days**. Aggregated procurement sums converge from bimodal (kurtosis $-1.57$) to Gaussian (kurtosis $+0.09$), restoring normal budgeting for DISCOMs. |
| **Unit 5: Open-Source Software** | Python, NumPy, SciPy, Matplotlib | Dual-mode ingestion, zero-leakage, reproducible | Standalone Colab/local execution with zero warnings. |

---

## 🚀 How to Run the Notebook in Google Colab

1. Open Google Colab: [https://colab.research.google.com/](https://colab.research.google.com/)
2. Click **File -> Upload notebook**, and select:
   `academic_submission/notebooks/SSI_THM6242_Applied_Probability_Project.ipynb`
3. Run all cells (`Ctrl + F9` or **Runtime -> Run all**).
4. The notebook automatically detects Colab and fetches the synchronized dataset directly from the GitHub repository raw URL. All derivations, tables, hand-solved checks, and plots will execute seamlessly.
