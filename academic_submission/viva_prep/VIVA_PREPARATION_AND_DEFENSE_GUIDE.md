# Symbiosis Statistical Institute [SSI] | Course THM6242: Applied Probability Distributions
## Comprehensive Viva Preparation, Defense Guide & Theory Master Sheet
**Candidate / Group:** Group 05 / Individual PRN  
**Course Instructor:** Dr. Monika Vishnoi, Assistant Professor, SSI  
**Project Title:** Empirical Characterization and Probabilistic Modeling of Price Formation, Extreme Volatility, and Daily Spike Dynamics in the Indian Electricity Market (IEX)  
**Associated Capstone Project:** Multi-Horizon Energy Market Intelligence Platform (`https://github.com/arcanekrishna/energy`)

---

## 1. Top Viva Questions Anticipated from Dr. Monika Vishnoi

### Q1: "Why did you choose the Gamma and Weibull distributions for electricity prices instead of the Normal distribution?"
**Answer:**
> "Wholesale electricity clearing prices violate classical Normal distribution assumptions in three fundamental physical ways:
> 1. **Strict Non-Negativity & Positive Skewness:** Electricity prices cannot drop below zero in normal operation (except under rare negative bidding rules) and exhibit positive right-tail skewness ($g_1 = +0.235$ on raw prices, rising sharply in unconstrained sub-periods). A symmetric Gaussian distribution assigns non-zero probability mass to negative prices, which is unphysical.
> 2. **Heavy Right Tails:** Generating assets have physical ramp limits and sudden failure rates. When solar drops at sunset, supply is inelastic, creating exponential or power-law price surges. The Gamma distribution ($\alpha \approx 1.91, \theta \approx 2952$) and Weibull distribution ($c \approx 1.58, \lambda \approx 6272$) naturally have non-negative supports $[0, \infty)$ and accommodate moderate to heavy right tails.
> 3. **Heteroscedasticity across Regimes:** As we showed in our Welch's $t$-test and $F$-test, the variance during the evening ramp ($s^2 \approx 7.87 \times 10^6$) is nearly six times higher than mid-day solar hours ($s^2 \approx 1.35 \times 10^6$), requiring flexible shape and scale parameterizations."

---

### Q2: "Why did the Poisson distribution fail for modeling daily price spikes, and why did the Negative Binomial succeed?"
**Answer:**
> "The Poisson distribution has a strict mathematical property known as **equidispersion**, where the theoretical variance must equal the theoretical mean ($\text{Var}(K) = E[K] = \lambda$, dispersion ratio $= 1.0$).
> In our empirical analysis of 31 trading days (96 blocks/day), counting spikes with $P_{RTM} \ge ₹7,000/\text{MWh}$:
> - The sample mean was $\bar{k} = 35.032$ spikes/day.
> - The sample variance was $s_k^2 = 718.566$ $(\text{spikes/day})^2$.
> - This produces an empirical **Dispersion Ratio** of:
>   $$\frac{s_k^2}{\bar{k}} = \frac{718.566}{35.032} = 20.512$$
> This indicates **extreme overdispersion** ($\text{Var} \gg \text{Mean}$).
> 
> **Physical Reason:** Spikes in the power grid do not arrive independently like classical telephone calls. Instead, when a major thermal unit trips or when solar generation collapses at sunset, the resulting transmission congestion and generation deficit persist across multiple consecutive 15-minute blocks. This intra-day clustering creates contagion.
> 
> **Mathematical Solution:** The Negative Binomial distribution can be derived as a **Gamma-Poisson mixture**, where the Poisson arrival rate $\Lambda$ is itself a random variable following a Gamma distribution $\Lambda \sim \text{Gamma}(r, \frac{1-p}{p})$. Its theoretical variance is:
> $$\text{Var}(K) = \frac{r(1-p)}{p^2} = E[K] + \frac{(E[K])^2}{r} > E[K]$$
> Using our from-scratch Method of Moments estimators ($\hat{p} = 0.0488, \hat{r} = 1.795$), the Negative Binomial variance matched the empirical variance of 718.566 exactly!"

---

### Q3: "Walk me through your hand-solved numerical example. How did you compute the moments and Method of Moments parameters?"
**Answer:**
> "We selected a representative 5-observation mini-sample:
> $$\mathcal{S} = \{2500, 3200, 4800, 7500, 10000\} \text{ ₹/MWh}$$
> 
> 1. **Sample Mean:**
>    $$\bar{x} = \frac{2500 + 3200 + 4800 + 7500 + 10000}{5} = \frac{28,000}{5} = 5,600.0 \text{ ₹/MWh}$$
> 
> 2. **Sum of Squared Deviations (Degrees of Freedom = 4):**
>    - $d_1 = 2500 - 5600 = -3100 \implies d_1^2 = 9,610,000$
>    - $d_2 = 3200 - 5600 = -2400 \implies d_2^2 = 5,760,000$
>    - $d_3 = 4800 - 5600 = -800 \implies d_3^2 = 640,000$
>    - $d_4 = 7500 - 5600 = +1900 \implies d_4^2 = 3,610,000$
>    - $d_5 = 10000 - 5600 = +4400 \implies d_5^2 = 19,360,000$
>    - $\sum d_i^2 = 38,980,000$
>    - $s^2 = \frac{38,980,000}{4} = 9,745,000.0 \implies s = \sqrt{9,745,000} \approx 3,121.70 \text{ ₹/MWh}$
> 
> 3. **Gamma Method of Moments Formulas:**
>    For $X \sim \text{Gamma}(\alpha, \beta)$ with $E[X] = \alpha/\beta$ and $\text{Var}(X) = \alpha/\beta^2$:
>    $$\hat{\alpha}_{\text{MoM}} = \frac{\bar{x}^2}{s^2} = \frac{(5600)^2}{9,745,000} = \frac{31,360,000}{9,745,000} \approx 3.2181$$
>    $$\hat{\beta}_{\text{MoM}} = \frac{\bar{x}}{s^2} = \frac{5600}{9,745,000} \approx 0.00057465 \implies \hat{\theta}_{\text{scale}} = \frac{1}{\hat{\beta}} \approx 1,740.18 \text{ ₹/MWh}$$
> 
> 4. **Verification of Law of Iterated Expectations:**
>    Splitting $\mathcal{S}$ at $T = 5000$: Low $\{2500, 3200, 4800\}$ ($n_1=3$, mean $= 3500$, $P=0.6$) and High $\{7500, 10000\}$ ($n_2=2$, mean $= 8750$, $P=0.4$).
>    $$E[E[X|\text{Group}]] = 0.6 \times 3500 + 0.4 \times 8750 = 2100 + 3500 = 5,600.0 \text{ ₹/MWh}$$
>    This matches the overall sample mean exactly!"

---

### Q4: "Your Chi-Square test rejected the Gamma distribution with $\chi^2 = 6,943.23$ ($p < 10^{-300}$). Does this mean your model is wrong?"
**Answer:**
> "No, this is actually the most insightful finding of our entire study, and it highlights a critical intersection between **probability theory** and **regulatory economics**!
> When we examine the cell-by-cell breakdown of the Chi-Square statistic across our 10 bins:
> - In bins 1 through 9 (from ₹0 to ₹9,000/MWh), the fitted Gamma distribution models the data well.
> - However, in Bin 10 ($[9,000, 10,000]$), the **Observed Count is 1,051**, whereas the continuous Gamma density expected only **136.35**!
> - Bin 10 alone contributes:
>   $$\frac{(1051 - 136.35)^2}{136.35} = 6,135.53$$
>   which is **88.37% of the entire Chi-Square statistic** ($\frac{6135.53}{6943.23} \times 100$)!
> 
> **The Real-Life Interpretation:**
> In India, the Central Electricity Regulatory Commission (CERC Order No. 4/SM/2022) mandates a **hard statutory price cap of ₹10,000/MWh**. In an unconstrained physical market, clearing prices would continue smoothly along a continuous Pareto or Fréchet tail into ₹15,000 or ₹20,000. But the legal ceiling forces all excess tail probability mass to accumulate at the upper boundary!
> A standard continuous density cannot fit this boundary point-mass without being formulated as a **Right-Censored / Truncated Compound Distribution**."

---

### Q5: "Explain the Law of Total Variance decomposition you derived and implemented in Unit 1. What does $\eta^2 = 49.10\%$ mean?"
**Answer:**
> "By Theorem 4.2:
> $$\text{Var}(Y) = E[\text{Var}(Y \mid X)] + \text{Var}(E[Y \mid X])$$
> - $Y = P_{RTM}$ is the Real-Time Market price.
> - $X$ is the Day-Ahead Market (DAM) physical imbalance ratio: $R = \frac{\text{DAM Purchase Bid MW}}{\text{DAM Sell Bid MW}}$.
> 
> In our empirical calculation across all 2,916 blocks:
> - Total Unconditional Variance: $\text{Var}(Y) = 12,454,419.98$
> - Expected Within-Regime Variance: $E[\text{Var}(Y \mid X)] = 6,339,197.40$ (50.90%)
> - Variance of Conditional Means: $\text{Var}(E[Y \mid X]) = 6,115,222.57$ (49.10%)
> - Sum $= 6,339,197.40 + 6,115,222.57 = 12,454,419.98$ (Exact match to 8 decimal places!).
> 
> **Meaning in Real Life:**
> $\eta^2 = \frac{\text{Var}(E[Y|X])}{\text{Var}(Y)} = 49.10\%$ is the coefficient of determination (correlation ratio). It means that **nearly half (49.1%) of the entire volatility in real-time balancing prices is already locked in 24 hours earlier** by the physical supply-demand deficit in the Day-Ahead market!
> Specifically, when $R > 1.25$, $E[Y|X] = ₹7,408.81/\text{MWh}$, compared to only ₹1,837.72/MWh during surplus hours—a **4.03x surge**!"

---

### Q6: "Explain the derivation of the order statistic distribution $F_{(n)}(x) = [F(x)]^n$ and why daily maximums hit the cap in 90.3% of days."
**Answer:**
> "Let $X_1, X_2, \dots, X_n$ be independent, identically distributed continuous random variables with CDF $F(x)$.
> The event that the sample maximum $X_{(n)} \le x$ occurs if and only if **every single individual observation $X_i \le x$**:
> $$P(X_{(n)} \le x) = P(X_1 \le x \cap X_2 \le x \cap \dots \cap X_n \le x)$$
> By mutual independence:
> $$P(X_{(n)} \le x) = \prod_{i=1}^n P(X_i \le x) = [F(x)]^n$$
> Differentiating using the chain rule yields the probability density function:
> $$f_{(n)}(x) = \frac{d}{dx} [F(x)]^n = n [F(x)]^{n-1} f(x)$$
> 
> **Why 90.3% of days hit the cap:**
> In our electricity dataset, $n = 96$ blocks per day.
> Even if the probability that a single 15-minute block hits the cap is modest—say $F(9999) = 0.975$ (meaning only a 2.5% chance of spiking in any single block):
> $$P(X_{(96)} \le 9999) = [0.975]^{96} \approx 0.087 = 8.7\%$$
> Thus, the probability of hitting the ceiling on a given day is:
> $$P(\text{Daily Cap Hit}) = 1 - 0.087 = 91.3\%$$
> Our empirical finding of **28 out of 31 days (90.32%)** matches this theoretical order statistics behavior!"

---

### Q7: "How does the Central Limit Theorem apply here when individual 15-minute price blocks are clearly bimodal and non-normal?"
**Answer:**
> "By the **Lindeberg-Lévy Central Limit Theorem**, given any sequence of i.i.d. random variables with finite mean $\mu$ and finite variance $\sigma^2$:
> $$Z_n = \frac{\sum_{i=1}^n X_i - n\mu}{\sigma \sqrt{n}} \xrightarrow{d} \mathcal{N}(0, 1) \quad \text{as } n \to \infty$$
> While a 15-minute price block ($n=1$) is severely non-normal (platykurtic, bimodal, kurtosis $g_2 = -1.571$), power distribution utilities (DISCOMs) procure power across aggregated blocks (hourly $n=4$, half-day $n=48$, full-day $n=96$).
> In our Monte Carlo simulation with $B = 3000$ bootstrap draws:
> - At $n = 1$: Skewness $= +0.235$, Kurtosis $= -1.571$ (Bimodal).
> - At $n = 4$: Skewness drops to $+0.191$, Kurtosis drops to $-0.293$.
> - At $n = 16$: Skewness $= +0.060$, Kurtosis $= -0.215$.
> - At $n = 96$ (Full day): Skewness $= +0.057$, Kurtosis $= +0.094$ (Virtually indistinguishable from a standard normal Gaussian!).
> 
> **Financial Meaning:** Even though spot market trading at 15-minute intervals is wildly non-linear, daily aggregated procurement budgets obey Gaussian laws, allowing utilities to use linear Gaussian Value-at-Risk (VaR) models for multi-day budget planning."

---

### Q8: "How does this academic submission relate to your larger GitHub Capstone System?"
**Answer:**
> "Our capstone repository (`https://github.com/arcanekrishna/energy`) is a complete, multi-horizon automated market intelligence and risk platform featuring LightGBM machine learning forecasters, split conformal prediction intervals, and a FastAPI interactive dashboard.
> However, **machine learning models cannot operate as ungrounded black boxes in safety-critical power grids**.
> This academic project provides the **theoretical probability foundation** that justifies and parameterizes our engineering architecture:
> 1. The **Gamma and Weibull shape and dispersion metrics** dictate the quantile loss pinball targets ($q_{10}, q_{50}, q_{90}$) in `src/risk_engine/quantile_models.py`.
> 2. The **Negative Binomial overdispersion parameters** guide the probability thresholding and isotonic calibration of our GBDT Stress Classifier in `src/risk_engine/stress_classifier.py`.
> 3. The **Law of Total Variance conditional regimes** provide the exact stratification required by our Split Conformal Prediction engine (`src/risk_engine/conformal.py`) to guarantee valid 90% coverage intervals without under-covering during evening ramp stress.
> In short, this academic component is the theoretical mathematical engine behind the practical software system!"

---

## 2. Theory Review Master Sheet (Units 1 to 4)

| Concept | Formal Mathematical Definition | Mean & Variance Formulas | Role in Our Energy Project |
| :--- | :--- | :--- | :--- |
| **Law of Iterated Expectations** | $E[Y] = E[E[Y \mid X]] = \sum_x E[Y \mid X=x] P(X=x)$ | $E[E[Y \mid X]] = E[Y]$ | Verifies that weighted conditional mean prices across market regimes equal the overall market clearing mean (₹5,596.76). |
| **Law of Total Variance** | $\text{Var}(Y) = E[\text{Var}(Y \mid X)] + \text{Var}(E[Y \mid X])$ | Partition of total variance into within-group and between-group components | Quantifies that 49.10% of real-time price variance is deterministic from day-ahead supply-demand imbalance queues. |
| **Poisson Distribution** | $P(K=k) = \frac{\lambda^k e^{-\lambda}}{k!}, \quad k \in \{0, 1, 2, \dots\}$ | $E[K] = \lambda$<br>$\text{Var}(K) = \lambda$ | Serves as the benchmark null model for price spike arrival; rejected due to severe overdispersion ($s^2/\bar{k} = 20.51$). |
| **Negative Binomial** | $P(K=k) = \frac{\Gamma(k+r)}{k! \Gamma(r)} p^r (1-p)^k$ | $E[K] = \frac{r(1-p)}{p}$<br>$\text{Var}(K) = \frac{r(1-p)}{p^2}$ | Models clustered price spike frequency as a Gamma-Poisson mixture ($r=1.795, p=0.0488$). |
| **Gamma Distribution** | $f(x) = \frac{\beta^\alpha}{\Gamma(\alpha)} x^{\alpha-1} e^{-\beta x}, \quad x > 0$ | $E[X] = \frac{\alpha}{\beta}$<br>$\text{Var}(X) = \frac{\alpha}{\beta^2}$ | Continuous model for wholesale prices ($\alpha=1.91, \theta=2952.85$); score solved via digamma function $\psi(\alpha)$. |
| **Weibull Distribution** | $f(x) = \frac{c}{\lambda} \left(\frac{x}{\lambda}\right)^{c-1} e^{-(x/\lambda)^c}, \quad x \ge 0$ | $E[X] = \lambda \Gamma(1 + 1/c)$<br>$\text{Var}(X) = \lambda^2 [\Gamma(1+2/c) - \Gamma^2(1+1/c)]$ | Continuous model benchmarking heavy tails ($c=1.5831, \lambda=6272.61$). |
| **Chi-Square ($\chi^2$) Test** | $\chi^2 = \sum_{j=1}^m \frac{(O_j - E_j)^2}{E_j} \sim \chi^2(m - 1 - p)$ | $E[\chi^2] = df$<br>$\text{Var}(\chi^2) = 2 \cdot df$ | Evaluates goodness-of-fit; reveals 88.37% of test statistic arises from CERC ₹10,000 regulatory cap accumulation. |
| **Welch's $t$-Test** | $t = \frac{\bar{X}_1 - \bar{X}_2}{\sqrt{s_1^2/n_1 + s_2^2/n_2}}$ | Standardized mean difference under unequal variances | Proves Evening Ramp prices are statistically higher than Mid-day Solar prices ($t = 46.80, p < 10^{-200}$). |
| **Two-Sample $F$-Test** | $F = \frac{s_1^2}{s_2^2} \sim F(n_1-1, n_2-1)$ | Variance ratio under normal sampling | Proves Evening price volatility is 5.80x higher than Solar mid-day ($p < 10^{-15}$), establishing heteroscedasticity. |
| **Order Statistics** | $F_{(n)}(x) = [F(x)]^n$<br>$f_{(n)}(x) = n [F(x)]^{n-1} f(x)$ | Distribution of sample extrema $X_{(n)} = \max_i X_i$ | Explains why daily maximum price hits the ₹10,000 ceiling in 90.3% of days when $n=96$. |
| **Central Limit Theorem** | $Z_n = \frac{S_n - n\mu}{\sigma \sqrt{n}} \xrightarrow{d} \mathcal{N}(0, 1)$ | Asymptotic convergence to Gaussian bell curve | Explains how daily aggregated DISCOM procurement expenditure ($n=96$) converges to normality despite non-normal 15-min blocks. |

---

## 3. Code Line-by-Line Defense

When asked: *"Explain this line of your code"*:

1. **Digamma Inversion for Gamma MLE:**
   ```python
   def gamma_mle_eq(a):
       return np.log(a) - psi(a) - (np.log(x_bar) - np.mean(np.log(prices_pos)))
   sol = root_scalar(gamma_mle_eq, bracket=[0.1, 10.0], method='brentq')
   ```
   *Explanation:* The score equation for the Gamma shape parameter $\alpha$ is $\frac{\partial \ln L}{\partial \alpha} = N \ln(\frac{\alpha}{\bar{x}}) - N \psi(\alpha) + \sum \ln x_i = 0$. Dividing by $N$ gives $\ln \alpha - \psi(\alpha) = \ln \bar{x} - \frac{1}{N}\sum \ln x_i$. This transcendental equation has no closed-form solution. We define the root-finding function `gamma_mle_eq(a)` and solve for $\hat{\alpha}$ using Brent's method over the bracket $[0.1, 10.0]$.

2. **First-Principles Chi-Square Test Statistic:**
   ```python
   exp_counts = n_pos * np.diff(stats.gamma.cdf(bin_edges, a_mle, scale=scale_mle))
   chi2_stat = np.sum((obs_counts - exp_counts)**2 / exp_counts)
   ```
   *Explanation:* `np.diff(stats.gamma.cdf(...))` calculates the theoretical probability mass in each bin $[b_{j-1}, b_j)$ under the null hypothesis. Multiplying by total sample size $N$ gives expected frequency $E_j$. We then compute Pearson's normalized squared deviations $\frac{(O_j - E_j)^2}{E_j}$ and sum them up to obtain the $\chi^2$ statistic.

3. **Law of Total Variance Decomposition:**
   ```python
   e_var = np.sum(weights * cond_vars) # E[Var(Y|X)]
   var_e = np.sum(weights * (cond_means - overall_mean)**2) # Var(E[Y|X])
   ```
   *Explanation:* `e_var` computes the expected unexplained variance within regimes $\sum P(X=r) \sigma_r^2$. `var_e` computes the variance between conditional expectations $\sum P(X=r) (\mu_r - \mu)^2$. Their sum reconstructs total unconditional variance $\text{Var}(Y)$ with 100% precision.
