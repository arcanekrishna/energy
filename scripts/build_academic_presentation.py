import os
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)  # 16:9 Widescreen
    prs.slide_height = Inches(7.5)

    blank_layout = prs.slide_layouts[6]

    # Color Palette: Deep Blue & Modern Accents
    c_navy = RGBColor(11, 37, 89)      # #0B2559
    c_blue = RGBColor(31, 73, 125)     # #1F497D
    c_light_bg = RGBColor(245, 248, 252) # #F5F8FC
    c_accent = RGBColor(230, 81, 0)    # Orange accent #E65100
    c_dark = RGBColor(33, 33, 33)      # #212121
    c_white = RGBColor(255, 255, 255)
    c_gray = RGBColor(110, 110, 110)

    def add_header(slide, title_text, category_text="SYMBIOSIS STATISTICAL INSTITUTE | THM6242"):
        # Header banner shape
        banner = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(1.1))
        banner.fill.solid()
        banner.fill.fore_color.rgb = c_navy
        banner.line.color.rgb = c_navy

        # Category text (small top)
        tx_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.12), Inches(11.7), Inches(0.3))
        tf = tx_box.text_frame
        tf.word_wrap = True
        p_cat = tf.paragraphs[0]
        p_cat.text = category_text.upper()
        p_cat.font.name = "Calibri"
        p_cat.font.size = Pt(10)
        p_cat.font.bold = True
        p_cat.font.color.rgb = RGBColor(180, 205, 240)

        # Title text
        p_title = tf.add_paragraph()
        p_title.text = title_text
        p_title.font.name = "Calibri"
        p_title.font.size = Pt(22)
        p_title.font.bold = True
        p_title.font.color.rgb = c_white

        # Subtle bottom line
        accent_line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(1.08), Inches(13.333), Inches(0.04))
        accent_line.fill.solid()
        accent_line.fill.fore_color.rgb = c_accent
        accent_line.line.color.rgb = c_accent

        # Footer
        footer_box = slide.shapes.add_textbox(Inches(0.8), Inches(7.1), Inches(11.7), Inches(0.3))
        tf_f = footer_box.text_frame
        p_f = tf_f.paragraphs[0]
        p_f.text = "THM6242: Applied Probability Distributions | Guide: Dr. Monika Vishnoi | SSI Batch 2026-28"
        p_f.font.name = "Calibri"
        p_f.font.size = Pt(10)
        p_f.font.color.rgb = c_gray

    # =========================================================================
    # SLIDE 1: TITLE SLIDE
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = c_navy
    bg1.line.color.rgb = c_navy

    # Accent decorative bar
    bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.0), Inches(1.5), Inches(0.15), Inches(4.5))
    bar.fill.solid()
    bar.fill.fore_color.rgb = c_accent
    bar.line.color.rgb = c_accent

    t_box = s1.shapes.add_textbox(Inches(1.4), Inches(1.4), Inches(11.0), Inches(4.8))
    tf1 = t_box.text_frame
    tf1.word_wrap = True

    p = tf1.paragraphs[0]
    p.text = "SYMBIOSIS STATISTICAL INSTITUTE [SSI]"
    p.font.name = "Calibri"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = RGBColor(190, 215, 255)

    p = tf1.add_paragraph()
    p.text = "Applied Probability Distributions (THM6242) — Internal Component IV"
    p.font.name = "Calibri"
    p.font.size = Pt(13)
    p.font.color.rgb = RGBColor(220, 220, 220)
    p.space_after = Pt(20)

    p = tf1.add_paragraph()
    p.text = "Empirical Characterization & Probabilistic Modeling\nof Price Formation, Volatility & Spike Dynamics\nin the Indian Electricity Market (IEX)"
    p.font.name = "Calibri"
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = c_white
    p.space_after = Pt(28)

    p = tf1.add_paragraph()
    p.text = "Author / Candidate: Group 05 / Student PRN  |  M.Sc. Applied Statistics & Data Science (SEM-I)\nSubject Teacher & Guide: Dr. Monika Vishnoi, Assistant Professor, SSI\nAssociated Capstone Repo: https://github.com/arcanekrishna/energy"
    p.font.name = "Calibri"
    p.font.size = Pt(13)
    p.font.color.rgb = RGBColor(200, 220, 245)

    # =========================================================================
    # SLIDE 2: THE REAL-LIFE PROBLEM
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_header(s2, "The Real-Life Problem: Non-Storability & Renewable Intermittency")
    
    tb2 = s2.shapes.add_textbox(Inches(0.8), Inches(1.4), Inches(11.7), Inches(5.4))
    tf2 = tb2.text_frame
    tf2.word_wrap = True

    def add_bullet(tf, title, desc, bold=True, size=15, space=12):
        p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
        r1 = p.add_run()
        r1.text = title + " "
        r1.font.bold = bold
        r1.font.size = Pt(size)
        r1.font.color.rgb = c_navy
        r2 = p.add_run()
        r2.text = desc
        r2.font.size = Pt(size)
        r2.font.color.rgb = c_dark
        p.space_after = Pt(space)

    add_bullet(tf2, "• Physical Nature of Electricity:", "Electric power cannot be economically stored at grid scale; generation must continuously match demand every single second to maintain grid frequency at 50 Hz.")
    add_bullet(tf2, "• The Solar Duck Curve Challenge:", "India's massive solar rollout creates huge daytime generation surplus (Blocks 40–60), collapsing prices. But when solar drops at sunset, net demand ramps up by >25,000 MW within 90 minutes.")
    add_bullet(tf2, "• Evening Ramp Stress & Price Spikes:", "Thermal power plants face ramp-rate physical limits and hydro is seasonally constrained. As a result, Real-Time Market (RTM) clearing prices explode to the regulatory ceiling.")
    add_bullet(tf2, "• Central Electricity Regulatory Commission (CERC) Price Ceiling:", "Order No. 4/SM/2022 imposes a hard regulatory price cap of ₹10,000/MWh, truncating the natural continuous distribution.")
    add_bullet(tf2, "• Breakdown of Gaussian Financial Assumptions:", "Traditional Normal distribution assumptions fail completely. We need rigorous probability models to handle heavy tails, overdispersed spike counts, and regulatory boundaries.")

    # =========================================================================
    # SLIDE 3: RESEARCH OBJECTIVES & SYLLABUS MAPPING
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_header(s3, "Research Objectives: Comprehensive Syllabus Mapping")

    tb3 = s3.shapes.add_textbox(Inches(0.8), Inches(1.3), Inches(11.7), Inches(5.5))
    tf3 = tb3.text_frame
    tf3.word_wrap = True

    add_bullet(tf3, "Unit 1: Expectation and Conditional Expectation", "Derive and verify the Law of Iterated Expectations E[E[Y|X]] = E[Y] and the Law of Total Variance Var(Y) = E[Var(Y|X)] + Var(E[Y|X]) using Day-Ahead Market imbalance regimes.")
    add_bullet(tf3, "Unit 2: Discrete Distributions (Count Process)", "Model the daily count of extreme price spikes (K: blocks >= ₹7,000/MWh). Formulate Poisson vs. Negative Binomial from scratch to test for overdispersion.")
    add_bullet(tf3, "Unit 2: Continuous Distributions (Price Densities)", "Derive and fit Two-Parameter Gamma and Weibull densities on positive wholesale clearing prices using Method of Moments and Maximum Likelihood (digamma inversion).")
    add_bullet(tf3, "Unit 3: Sampling Distributions (χ², t, F)", "Implement Pearson's Chi-Square Goodness-of-Fit test from first principles. Conduct Welch's t-test for Solar vs. Evening regimes, and F-test for variance equality.")
    add_bullet(tf3, "Unit 4: Order Statistics & Central Limit Theorem", "Derive the distribution of daily peak price X_(96) = max_{1<=i<=96} X_i. Demonstrate Gaussian convergence of portfolio procurement sums via Monte Carlo CLT simulation.")
    add_bullet(tf3, "Unit 5: Open-Source Software & From-Scratch Protocol", "Write all primary estimation, testing, and simulation routines in native NumPy; use scipy.stats solely for benchmark cross-verification.")

    # =========================================================================
    # SLIDE 4: THE DATASET & EXPLORATORY ANALYSIS
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_header(s4, "Dataset & Exploratory Analysis (2,916 Synchronized Blocks)")

    # Left text box
    tb4 = s4.shapes.add_textbox(Inches(0.8), Inches(1.3), Inches(5.8), Inches(5.5))
    tf4 = tb4.text_frame
    tf4.word_wrap = True

    add_bullet(tf4, "• Source:", "Indian Energy Exchange (IEX) & Grid-India (NLDC).", size=13, space=8)
    add_bullet(tf4, "• Scope:", "2,916 fifteen-minute blocks (31 days: Oct 03 – Nov 02, 2026).", size=13, space=8)
    add_bullet(tf4, "• Key Variables:", "dam_mcp, rtm_mcp, dam_purchase_bid_mw, dam_sell_bid_mw.", size=13, space=8)
    add_bullet(tf4, "• Summary Moments:", "Mean x̄ = ₹5,596.76/MWh | Std s = ₹3,529.69/MWh | Variance s² = 12.46 × 10⁶.", size=13, space=8)
    add_bullet(tf4, "• Skewness & Kurtosis:", "Skewness g₁ = +0.235 (Right-tailed) | Kurtosis g₂ = -1.571 (Platykurtic/Bimodal).", size=13, space=8)
    add_bullet(tf4, "• CERC Price Cap Saturation:", "828 blocks (28.40% of all intervals) clear at the exact statutory ceiling of ₹10,000/MWh.", size=13, space=8)

    # Right Image
    fig1_p = "/Users/krishnagupta/Downloads/inte/indian_power_market/academic_submission/figures/fig1_diurnal_price_duck_curve.png"
    if os.path.exists(fig1_p):
        s4.shapes.add_picture(fig1_p, Inches(6.8), Inches(1.5), Inches(5.8), Inches(4.8))

    # =========================================================================
    # SLIDE 5: HAND-SOLVED NUMERICAL EXAMPLE
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    add_header(s5, "Hand-Solved Numerical Example (SSI Rubric Requirement)")

    tb5 = s5.shapes.add_textbox(Inches(0.8), Inches(1.3), Inches(11.7), Inches(5.5))
    tf5 = tb5.text_frame
    tf5.word_wrap = True

    add_bullet(tf5, "Mini-Sample:", "S = {2500, 3200, 4800, 7500, 10000} ₹/MWh (n = 5 representative observations)", size=14, space=10)
    add_bullet(tf5, "1. Sample Moments:", "Mean x̄ = 28,000 / 5 = 5,600.0 ₹/MWh  |  Sum of Squared Deviations ∑(x_i - x̄)² = 38,980,000  |  s² = 38,980,000 / 4 = 9,745,000.0 (s = 3,121.70)", size=14, space=10)
    add_bullet(tf5, "2. Method of Moments (Gamma):", "α̂_MoM = x̄² / s² = (5,600)² / 9,745,000 = 3.2181  |  Scale θ̂_MoM = s² / x̄ = 9,745,000 / 5,600 = 1,740.18 ₹/MWh", size=14, space=10)
    add_bullet(tf5, "3. Law of Iterated Expectations:", "Partition S by T = 5000: Low {2500, 3200, 4800} (n=3, mean=3,500) and High {7500, 10000} (n=2, mean=8,750).\nE[E[X|G]] = (3/5 × 3,500) + (2/5 × 8,750) = 2,100 + 3,500 = 5,600.0 ₹/MWh (Exact match to x̄!)", size=14, space=10)
    add_bullet(tf5, "4. Chi-Square Goodness-of-Fit Hand Table:", "3 Bins: [0, 4000), [4000, 7000), [7000, 12000]. Observed O = [2, 1, 2]. Hypothesized Expected E = [1.75, 1.75, 1.50].\nχ² = (2 - 1.75)²/1.75 + (1 - 1.75)²/1.75 + (2 - 1.50)²/1.50 = 0.0357 + 0.3214 + 0.1667 = 0.5238 < χ²_crit(df=2) = 5.991.", size=14, space=10)

    # =========================================================================
    # SLIDE 6: UNIT 1 - EXPECTATION & TOTAL VARIANCE
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    add_header(s6, "Unit 1: Expectation, Conditional Expectation & Total Variance")

    tb6 = s6.shapes.add_textbox(Inches(0.8), Inches(1.3), Inches(5.8), Inches(5.5))
    tf6 = tb6.text_frame
    tf6.word_wrap = True

    add_bullet(tf6, "• Conditioning Variable:", "Day-Ahead Market Imbalance Ratio R = DAM Purchase / DAM Sell.", size=13, space=8)
    add_bullet(tf6, "• Deficit Regime (R > 1.25):", "N = 1,885 (64.6%) | E[Y|X] = ₹7,408.81/MWh | Std = ₹3,030.66", size=13, space=8)
    add_bullet(tf6, "• Balanced Regime [0.8, 1.25]:", "N = 398 (13.7%) | E[Y|X] = ₹2,993.12/MWh | Std = ₹1,080.06", size=13, space=8)
    add_bullet(tf6, "• Surplus Regime (R < 0.8):", "N = 633 (21.7%) | E[Y|X] = ₹1,837.72/MWh | Std = ₹1,065.62", size=13, space=8)
    add_bullet(tf6, "• Law of Total Variance:", "Total Var = 12,454,420 (₹/MWh)²\nE[Var(Y|X)] = 6,339,197 (50.90% Within-Regime)\nVar(E[Y|X]) = 6,115,223 (49.10% Between-Regime)", size=13, space=8)
    add_bullet(tf6, "• Physical Meaning (η² = 49.1%):", "Nearly half of all real-time price variance is already locked into day-ahead bid queues!", size=13, space=8)

    fig2_p = "/Users/krishnagupta/Downloads/inte/indian_power_market/academic_submission/figures/fig2_conditional_expectation_regimes.png"
    if os.path.exists(fig2_p):
        s6.shapes.add_picture(fig2_p, Inches(6.8), Inches(1.5), Inches(5.8), Inches(4.8))

    # =========================================================================
    # SLIDE 7: UNIT 2 - DISCRETE SPIKE FREQUENCY
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    add_header(s7, "Unit 2: Discrete Distribution Modeling — Poisson vs. Negative Binomial")

    tb7 = s7.shapes.add_textbox(Inches(0.8), Inches(1.3), Inches(5.8), Inches(5.5))
    tf7 = tb7.text_frame
    tf7.word_wrap = True

    add_bullet(tf7, "• Random Quantity:", "Daily spike count K = ∑ 𝕀(P_RTM >= ₹7,000/MWh) across 96 blocks (D = 31 days).", size=13, space=8)
    add_bullet(tf7, "• Empirical Moments:", "Mean k̄ = 35.032 spikes/day | Variance s_k² = 718.566.", size=13, space=8)
    add_bullet(tf7, "• Overdispersion Diagnosis:", "Dispersion Ratio = s_k² / k̄ = 20.512 >> 1.0 (Severe Overdispersion!).", size=13, space=8)
    add_bullet(tf7, "• Poisson Model Failure:", "Poisson assumes Var = Mean = 35.032. It fails catastrophically because price spikes are clustered during evening ramp hours.", size=13, space=8)
    add_bullet(tf7, "• Negative Binomial Success:", "Method of Moments from scratch:\np̂ = k̄ / s_k² = 0.0488 | r̂ = k̄² / (s_k² - k̄) = 1.795.\nTheoretical Variance = 718.566 (Exact match).", size=13, space=8)

    fig3_p = "/Users/krishnagupta/Downloads/inte/indian_power_market/academic_submission/figures/fig3_discrete_spike_poisson_vs_negbinom.png"
    if os.path.exists(fig3_p):
        s7.shapes.add_picture(fig3_p, Inches(6.8), Inches(1.5), Inches(5.8), Inches(4.8))

    # =========================================================================
    # SLIDE 8: UNIT 2 - CONTINUOUS PRICE DENSITIES
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    add_header(s8, "Unit 2: Continuous Distribution Modeling — Gamma vs. Weibull")

    tb8 = s8.shapes.add_textbox(Inches(0.8), Inches(1.3), Inches(5.8), Inches(5.5))
    tf8 = tb8.text_frame
    tf8.word_wrap = True

    add_bullet(tf8, "• Dataset:", "Positive clearing prices (P > 10, N = 2,887 blocks, x̄ = ₹5,652.88, s = ₹3,501.99).", size=13, space=8)
    add_bullet(tf8, "• Scratch Gamma MoM:", "α̂ = x̄² / s² = 2.6052 | θ̂ = s² / x̄ = 2,169.86 ₹/MWh.", size=13, space=8)
    add_bullet(tf8, "• Scratch Gamma MLE:", "Solved ln α - ψ(α) = ln x̄ - (1/N)∑ln x_i via Brent root-finding:\nShape α̂ = 1.9144 | Scale θ̂ = 2,952.85 ₹/MWh.", size=13, space=8)
    add_bullet(tf8, "• SciPy Cross-Verification:", "stats.gamma.fit() yields α̂ = 1.9144, θ̂ = 2,952.85 (|Discrepancy| < 10⁻⁸).", size=13, space=8)
    add_bullet(tf8, "• Weibull MLE Benchmark:", "Shape ĉ = 1.5831 | Scale λ̂ = 6,272.61 ₹/MWh.", size=13, space=8)
    add_bullet(tf8, "• Physical Truncation Spike:", "Both densities fit the interior spread, but CERC ₹10,000 regulatory ceiling forces point-mass accumulation at the upper boundary.", size=13, space=8)

    fig4_p = "/Users/krishnagupta/Downloads/inte/indian_power_market/academic_submission/figures/fig4_continuous_price_gamma_weibull.png"
    if os.path.exists(fig4_p):
        s8.shapes.add_picture(fig4_p, Inches(6.8), Inches(1.5), Inches(5.8), Inches(4.8))

    # =========================================================================
    # SLIDE 9: UNIT 3 - CHI-SQUARE GOODNESS-OF-FIT
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    add_header(s9, "Unit 3: Pearson's Chi-Square Goodness-of-Fit Test")

    tb9 = s9.shapes.add_textbox(Inches(0.8), Inches(1.3), Inches(11.7), Inches(5.5))
    tf9 = tb9.text_frame
    tf9.word_wrap = True

    add_bullet(tf9, "Hypotheses:", "H₀: Market clearing price X follows Gamma(α̂ = 1.9144, θ̂ = 2952.85)  vs.  H₁: X does not follow Gamma.", size=14, space=10)
    add_bullet(tf9, "First-Principles Binning Protocol:", "10 equiprobable/equidistant bins spanning [0, 10001]. Expected frequencies computed as E_j = N · [F(b_j) - F(b_{j-1})]. All E_j >= 5 (Cochran's rule satisfied).", size=14, space=10)
    add_bullet(tf9, "Test Statistic Calculation:", "χ² = ∑_{j=1}^{10} (O_j - E_j)² / E_j = 6,943.23  |  df = 10 - 1 - 2 = 7  |  p-value < 10⁻³⁰⁰ (Reject H₀).", size=14, space=10)
    add_bullet(tf9, "Critical Viva Insight (Why did Chi-Square reject H₀?):", "The rejection is driven almost entirely by the top bin [9000, 10000], which contributes 6,135.53 (88.37%) to the total test statistic! Observed = 1,051 vs Expected = 136.35.\nThis divergence is not an error in probability modeling—it represents the physical and regulatory reality of CERC's statutory ₹10,000/MWh price ceiling collapsing all tail mass into the boundary!", size=14, space=10)

    # =========================================================================
    # SLIDE 10: UNIT 3 - SAMPLING DISTRIBUTIONS (t & F TESTS)
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    add_header(s10, "Unit 3: Sampling Distributions — Welch's t-Test & Variance F-Test")

    tb10 = s10.shapes.add_textbox(Inches(0.8), Inches(1.3), Inches(11.7), Inches(5.5))
    tf10 = tb10.text_frame
    tf10.word_wrap = True

    add_bullet(tf10, "Physical Question:", "Are Real-Time Market prices during the Solar Mid-Day Duck Curve (Blocks 40–60) significantly lower than during the Evening Peak Ramp (Blocks 72–88)?", size=14, space=10)
    add_bullet(tf10, "Sample Comparison:", "• Solar Mid-Day (N₂ = 630): Mean x̄₂ = ₹1,815.98/MWh | Std s₂ = ₹1,164.29/MWh\n• Evening Peak (N₁ = 510): Mean x̄₁ = ₹8,021.44/MWh | Std s₁ = ₹2,805.00/MWh\nMean Price Differential: +₹6,205.46/MWh (4.42x surge!).", size=14, space=10)
    add_bullet(tf10, "Welch's Two-Sample t-Test (Unequal Variances):", "t_scratch = (x̄₁ - x̄₂) / √(s₁²/n₁ + s₂²/n₂) = 46.8031  |  df = 654.8  |  p-value = 1.975 × 10⁻²¹⁰.\nConclusion: Statistically overwhelming rejection of H₀ (Evening prices are decisively higher).", size=14, space=10)
    add_bullet(tf10, "Two-Sample F-Test for Variance Ratio (Heteroscedasticity):", "F_scratch = s₁² / s₂² = (2805.00)² / (1164.29)² = 5.8042  |  df₁ = 509, df₂ = 629  |  p-value = 1.110 × 10⁻¹⁶.\nConclusion: Evening ramp price variance is 5.80x greater than solar mid-day, proving extreme intra-day heteroscedasticity.", size=14, space=10)

    # =========================================================================
    # SLIDE 11: UNIT 4 - EXTREME VALUE ORDER STATISTICS
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    add_header(s11, "Unit 4: Extreme Value Order Statistics (Daily Max X_(96))")

    tb11 = s11.shapes.add_textbox(Inches(0.8), Inches(1.3), Inches(5.8), Inches(5.5))
    tf11 = tb11.text_frame
    tf11.word_wrap = True

    add_bullet(tf11, "• Mathematical Formulation:", "Daily maximum price X_(96) = max(X₁, ..., X₉₆).", size=13, space=8)
    add_bullet(tf11, "• Theoretical CDF Derivation:", "F_(96)(x) = P(all X_i <= x) = [F(x)]⁹⁶.\nDensity f_(96)(x) = 96 [F(x)]⁹⁵ f(x).", size=13, space=8)
    add_bullet(tf11, "• Empirical Cap Saturation:", "In 28 out of 31 trading days (90.32%), the daily peak price hits the CERC ceiling of ₹10,000/MWh!", size=13, space=8)
    add_bullet(tf11, "• Daily Max Moments:", "Mean = ₹9,726.79/MWh | Std = ₹888.72/MWh | Min = ₹6,029.81/MWh.", size=13, space=8)
    add_bullet(tf11, "• Grid Reliability Impact:", "Because n = 96 is large, [F(x)]⁹⁶ approaches zero for any sub-cap price. Hitting the cap is almost guaranteed daily, signaling structural peaking deficits.", size=13, space=8)

    fig5_p = "/Users/krishnagupta/Downloads/inte/indian_power_market/academic_submission/figures/fig5_order_statistics_daily_max.png"
    if os.path.exists(fig5_p):
        s11.shapes.add_picture(fig5_p, Inches(6.8), Inches(1.5), Inches(5.8), Inches(4.8))

    # =========================================================================
    # SLIDE 12: UNIT 4 - CENTRAL LIMIT THEOREM
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    add_header(s12, "Unit 4: Central Limit Theorem on Electricity Procurement Sums")

    tb12 = s12.shapes.add_textbox(Inches(0.8), Inches(1.3), Inches(5.8), Inches(5.5))
    tf12 = tb12.text_frame
    tf12.word_wrap = True

    add_bullet(tf12, "• Problem:", "15-minute price blocks are wildly non-normal, skewed, and bimodal. How can utilities forecast daily procurement budgets?", size=13, space=8)
    add_bullet(tf12, "• Lindeberg-Lévy CLT:", "Z_n = (S_n - nμ) / (σ√n) ---> N(0, 1) as n ---> ∞ for portfolio sum S_n = ∑_{i=1}^n X_i.", size=13, space=8)
    add_bullet(tf12, "• Empirical Convergence Tracking:", "• n = 1 (15-min): Skew = +0.235, Kurtosis = -1.571 (Bimodal)\n• n = 4 (1-hour): Skew = +0.191, Kurtosis = -0.293\n• n = 16 (4-hour): Skew = +0.060, Kurtosis = -0.215\n• n = 96 (Full-day): Skew = +0.057, Kurtosis = +0.094", size=13, space=8)
    add_bullet(tf12, "• Financial Takeaway:", "CLT restores Gaussianity for aggregated daily DISCOM procurement, validating classical Value-at-Risk (VaR) budgeting!", size=13, space=8)

    fig6_p = "/Users/krishnagupta/Downloads/inte/indian_power_market/academic_submission/figures/fig6_central_limit_theorem_convergence.png"
    if os.path.exists(fig6_p):
        s12.shapes.add_picture(fig6_p, Inches(6.8), Inches(1.5), Inches(5.8), Inches(4.8))

    # =========================================================================
    # SLIDE 13: KEY PYTHON CODE (FROM-SCRATCH NUMPY)
    # =========================================================================
    s13 = prs.slides.add_slide(blank_layout)
    add_header(s13, "Key Python Code: First-Principles NumPy Implementation")

    tb13 = s13.shapes.add_textbox(Inches(0.8), Inches(1.3), Inches(11.7), Inches(5.5))
    tf13 = tb13.text_frame
    tf13.word_wrap = True

    code_snip = (
        "# 1. Law of Total Variance Decomposition (Scratch NumPy)\n"
        "weights = np.array([len(p) / len(prices) for p in [deficit, balanced, surplus]])\n"
        "e_var = np.sum(weights * [np.var(p, ddof=0) for p in [deficit, balanced, surplus]]) # E[Var(Y|X)]\n"
        "var_e = np.sum(weights * ([np.mean(p) for p in [deficit, balanced, surplus]] - np.mean(prices))**2) # Var(E[Y|X])\n"
        "eta_squared = (var_e / np.var(prices, ddof=0)) * 100.0  # Returns 49.10%\n\n"
        "# 2. Negative Binomial Method of Moments (Scratch)\n"
        "p_hat_nb = mean_spikes / var_spikes                   # Returns 0.0488\n"
        "r_hat_nb = (mean_spikes**2) / (var_spikes - mean_spikes) # Returns 1.795\n\n"
        "# 3. Pearson Chi-Square Test Statistic from First Principles\n"
        "exp_counts = n_pos * np.diff(stats.gamma.cdf(bin_edges, a_mle, scale=scale_mle))\n"
        "chi2_stat = np.sum((obs_counts - exp_counts)**2 / exp_counts) # Returns 6943.23\n"
        "p_value = 1.0 - stats.chi2.cdf(chi2_stat, df=len(obs_counts) - 1 - 2) # df=7"
    )
    p_c = tf13.paragraphs[0]
    p_c.text = code_snip
    p_c.font.name = "Courier New"
    p_c.font.size = Pt(13)
    p_c.font.color.rgb = RGBColor(10, 40, 90)

    # =========================================================================
    # SLIDE 14: REAL-WORLD STAKEHOLDER TAKEAWAYS
    # =========================================================================
    s14 = prs.slides.add_slide(blank_layout)
    add_header(s14, "Real-World Interpretation for Power Sector Stakeholders")

    tb14 = s14.shapes.add_textbox(Inches(0.8), Inches(1.3), Inches(11.7), Inches(5.5))
    tf14 = tb14.text_frame
    tf14.word_wrap = True

    add_bullet(tf14, "1. Distribution Companies (DISCOMs):", "When Day-Ahead imbalance breaches 1.25, the conditional expected price is ₹7,408/MWh (4.03x surge). Utilities must hedge forward in the Day-Ahead Market rather than gambling on real-time spot purchases.", size=14, space=10)
    add_bullet(tf14, "2. Battery Storage (BESS) & Renewable IPPs:", "The Welch t-test (t = 46.80) and F-test (F = 5.80) prove a massive, statistically guaranteed ₹6,205/MWh diurnal arbitrage spread between solar charging and evening discharge.", size=14, space=10)
    add_bullet(tf14, "3. Grid System Operators (Grid-India / NLDC):", "Daily maximums hitting the cap in 90.3% of days signals acute physical ramping deficits. Ancillary reserves must be dispatched at least 90 minutes prior to sunset.", size=14, space=10)
    add_bullet(tf14, "4. Market Regulators (CERC):", "Chi-Square analysis proved that 88.37% of distribution divergence arises from cap accumulation at ₹10,000, signaling the need for market-based dynamic ramping capacity tariffs.", size=14, space=10)

    # =========================================================================
    # SLIDE 15: CONCLUSION & CAPSTONE INTEGRATION
    # =========================================================================
    s15 = prs.slides.add_slide(blank_layout)
    add_header(s15, "Conclusion, Capstone Integration & Academic References")

    tb15 = s15.shapes.add_textbox(Inches(0.8), Inches(1.3), Inches(11.7), Inches(5.5))
    tf15 = tb15.text_frame
    tf15.word_wrap = True

    add_bullet(tf15, "• Bridge to Production Capstone:", "This probability research directly powers our automated multi-horizon trading system (https://github.com/arcanekrishna/energy):\n- LightGBM Quantile Forecaster calibrated via Gamma/Weibull shape parameters.\n- Stress Classifier calibrated via Negative Binomial overdispersion thresholds.\n- Conformal Prediction interval widths dynamically scaled by conditional variance regimes.", size=13, space=8)
    add_bullet(tf15, "• Summary of Syllabus Mastery:", "Covered Unit 1 (Iterated Expectation & Total Variance), Unit 2 (Poisson/NB & Gamma/Weibull), Unit 3 (χ² GoF, Welch t, F-test), Unit 4 (Order Statistics & CLT), and Unit 5 (NumPy from scratch).", size=13, space=8)
    add_bullet(tf15, "• Academic References:", "[1] Casella & Berger (2002). Statistical Inference. [2] Hogg, McKean & Craig (2018). Introduction to Mathematical Statistics. [3] CERC (2022) Market Order No. 4/SM/2022. [4] Weron (2014) Electricity Price Forecasting.", size=13, space=8)
    add_bullet(tf15, "• Thank You!", "Questions & Viva Defense.", size=16, space=8)

    out_pptx = '/Users/krishnagupta/Downloads/inte/indian_power_market/academic_submission/presentation/Group05_Title05_Presentation.pptx'
    prs.save(out_pptx)
    print("Academic Presentation (.pptx) successfully created at:", out_pptx)

if __name__ == '__main__':
    create_presentation()
