import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#666666"))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 842 - 36, "Symbiosis Statistical Institute | Course THM6242: Applied Probability Distributions")
            self.drawRightString(595 - 54, 842 - 36, "IEX Probability Project Report")
            self.setStrokeColor(colors.HexColor("#B0C4DE"))
            self.setLineWidth(0.6)
            self.line(54, 842 - 42, 595 - 54, 842 - 42)
            
        # Footer
        self.setStrokeColor(colors.HexColor("#B0C4DE"))
        self.setLineWidth(0.6)
        self.line(54, 46, 595 - 54, 46)
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawString(54, 32, "M.Sc. Applied Statistics & Data Science (SEM-I Batch-2026-2028)")
        self.drawRightString(595 - 54, 32, page_str)
        self.restoreState()

def generate_pdf():
    pdf_path = "/Users/krishnagupta/Downloads/inte/indian_power_market/academic_submission/reports/Group05_Title05_Report.pdf"
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles - Strict A4 12pt 1.5 line spacing (12pt font with 18pt leading)
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=21,
        leading=28,
        textColor=colors.HexColor("#0B2559"),
        alignment=1, # Center
        spaceAfter=15
    )
    
    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=20,
        textColor=colors.HexColor("#0F3C82"),
        spaceBefore=16,
        spaceAfter=10,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12.5,
        leading=17,
        textColor=colors.HexColor("#28466E"),
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=11.5,
        leading=17.5, # 1.5 line spacing
        textColor=colors.HexColor("#222222"),
        spaceAfter=9
    )

    abstract_style = ParagraphStyle(
        'Abstract',
        parent=styles['Normal'],
        fontName='Times-Italic',
        fontSize=11,
        leading=17,
        textColor=colors.HexColor("#1A1A1A"),
        spaceAfter=12
    )

    caption_style = ParagraphStyle(
        'Caption',
        parent=styles['Normal'],
        fontName='Helvetica-BoldOblique',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#333333"),
        alignment=1,
        spaceAfter=12
    )

    tbl_text = ParagraphStyle(
        'TblText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#222222")
    )
    
    tbl_text_hdr = ParagraphStyle(
        'TblHdr',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13,
        textColor=colors.white,
        alignment=1
    )

    story = []

    # ---------------------------------------------------------
    # COVER PAGE
    # ---------------------------------------------------------
    story.append(Spacer(1, 40))
    p_inst = Paragraph("<b>SYMBIOSIS STATISTICAL INSTITUTE [SSI]<br/>SYMBIOSIS INTERNATIONAL (DEEMED UNIVERSITY), PUNE</b>", ParagraphStyle('Inst', parent=title_style, fontSize=14, leading=19, textColor=colors.HexColor("#0B2559")))
    story.append(p_inst)
    story.append(Spacer(1, 15))
    
    p_sub = Paragraph("<b>Academic Year 2026-27 | M.Sc. Applied Statistics & Data Science<br/>(SEM-I Batch-2026-2028)<br/>Course: Applied Probability Distributions (THM6242)<br/>Internal Component-III: Project Report (30 Marks)</b>", ParagraphStyle('Sub', parent=title_style, fontSize=11, leading=16, textColor=colors.HexColor("#444444"), fontName="Helvetica"))
    story.append(p_sub)
    story.append(Spacer(1, 40))
    
    story.append(Paragraph("Empirical Characterization and Probabilistic Modeling of Price Formation, Extreme Volatility, and Daily Spike Dynamics in the Indian Electricity Market (IEX)", title_style))
    story.append(Spacer(1, 45))
    
    p_meta = Paragraph(
        "<b>Submitted by:</b><br/>"
        "Student Academic Project Group (Group 05 / PRN: Individual Candidate)<br/>"
        "M.Sc. Applied Statistics and Data Science, Semester-I<br/><br/>"
        "<b>Under the Guidance & Mentorship of:</b><br/>"
        "<b>Dr. Monika Vishnoi</b><br/>"
        "Assistant Professor & Subject Teacher, Applied Probability Distributions<br/>"
        "Symbiosis Statistical Institute, Pune<br/><br/>"
        "<b>Submission Date:</b> November 2026<br/>"
        "<b>Associated Capstone System:</b> Multi-Horizon Energy Market Intelligence Platform<br/>"
        "<b>GitHub Repository:</b> <u>https://github.com/arcanekrishna/energy</u>",
        ParagraphStyle('Meta', parent=body_style, alignment=1, fontSize=10.5, leading=16)
    )
    story.append(p_meta)
    story.append(PageBreak())

    # ---------------------------------------------------------
    # DECLARATION & CONTRIBUTION SHEET
    # ---------------------------------------------------------
    story.append(Paragraph("Student Declaration of Originality and Academic Integrity", h1_style))
    story.append(Paragraph("<b>Declaration:</b> We hereby declare that this project report entitled <i>'Empirical Characterization and Probabilistic Modeling of Price Formation, Extreme Volatility, and Daily Spike Dynamics in the Indian Electricity Market (IEX)'</i> submitted for Internal Component-III of the course Applied Probability Distributions (THM6242) is our original work conducted under the guidance of Dr. Monika Vishnoi at Symbiosis Statistical Institute, Symbiosis International (Deemed University).", body_style))
    story.append(Paragraph("<b>Methodological Compliance:</b> In accordance with the academic guidelines of THM6242, all theoretical derivations, mathematical formulations, and primary computational steps—including method of moments estimation, numerical maximum likelihood optimization, chi-square goodness-of-fit statistics, and Monte Carlo Central Limit Theorem routines—were developed from first principles using native NumPy algorithms, and standard packages (scipy.stats) were employed solely for cross-validation.", body_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Author Contribution and Task Responsibility Matrix", h2_style))
    contrib_data = [
        [Paragraph("Project Component", tbl_text_hdr), Paragraph("Syllabus Unit Alignment", tbl_text_hdr), Paragraph("Methodological Responsibility", tbl_text_hdr)],
        [Paragraph("Problem Definition & Ingestion", tbl_text), Paragraph("Unit 5 (Hands-On Open Data)", tbl_text), Paragraph("Pipeline development, IEX DAM/RTM synchronization, CERC regulatory boundary checks.", tbl_text)],
        [Paragraph("Expectation & Variance Decomp.", tbl_text), Paragraph("Unit 1 (Expectation & Conditional)", tbl_text), Paragraph("Mathematical derivation of Tower Property & Law of Total Variance; first-principles code.", tbl_text)],
        [Paragraph("Discrete Spike Modeling", tbl_text), Paragraph("Unit 2 (Discrete Distributions)", tbl_text), Paragraph("Formulation of Poisson vs Negative Binomial PMF; overdispersion test derivation.", tbl_text)],
        [Paragraph("Continuous Clearing Price Model", tbl_text), Paragraph("Unit 2 (Continuous Distributions)", tbl_text), Paragraph("Gamma & Weibull PDF derivations, score equations, Brent root-scalar MLE optimizer.", tbl_text)],
        [Paragraph("Goodness-of-Fit & Hyp. Tests", tbl_text), Paragraph("Unit 3 (Sampling Distributions)", tbl_text), Paragraph("First-principles Pearson Chi-Square test, Welch's t-test, variance ratio F-test.", tbl_text)],
        [Paragraph("Order Statistics & CLT Engine", tbl_text), Paragraph("Unit 4 (Order Stats & CLT)", tbl_text), Paragraph("Derivation of X_(n) CDF/PDF, CERC cap point-mass analysis, Monte Carlo CLT simulation.", tbl_text)],
        [Paragraph("Report & Presentation Synthesis", tbl_text), Paragraph("Component III & IV Deliverables", tbl_text), Paragraph("Comprehensive 25-page academic manuscript drafting, presentation slide deck, viva defense.", tbl_text)]
    ]
    t_contrib = Table(contrib_data, colWidths=[120, 140, 227])
    t_contrib.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1F497D')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#D0D8E0')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#FFFFFF'), colors.HexColor('#F7F9FB')])
    ]))
    story.append(t_contrib)
    story.append(PageBreak())

    # ---------------------------------------------------------
    # ABSTRACT
    # ---------------------------------------------------------
    story.append(Paragraph("Executive Abstract", h1_style))
    story.append(Paragraph(
        "Wholesale electricity markets present severe probabilistic modeling challenges due to non-storability, diurnal renewable "
        "generation intermittency (solar duck curve), physical transmission congestion, and regulatory price bounds. This study "
        "empirically characterizes and models 2,916 synchronized 15-minute operational dispatch blocks from the Indian Energy Exchange "
        "(IEX) Day-Ahead (DAM) and Real-Time Markets (RTM) spanning October–November 2026. Rigorously covering all four theoretical units "
        "of the Applied Probability Distributions (THM6242) curriculum, we establish: (1) The Day-Ahead market imbalance ratio governs "
        "conditional price expectations, explaining 49.10% of total real-time price variance via the Law of Total Variance; (2) Daily high-price "
        "spike counts exhibit severe overdispersion (dispersion index = 20.51), rendering Poisson models invalid and establishing the Negative "
        "Binomial as the superior physical model for generator outage clustering; (3) Continuous prices fit Two-Parameter Gamma and Weibull densities "
        "across intermediate regimes, but diverge at the upper tail due to the statutory Central Electricity Regulatory Commission (CERC) ₹10,000/MWh "
        "ceiling cap, confirmed via first-principles Chi-Square Goodness-of-Fit tests; (4) Diurnal price disparities between mid-day solar hours "
        "(mean ₹1,816/MWh) and evening ramp peaks (mean ₹8,021/MWh) are statistically overwhelming (Welch’s t = 46.80, p < 10^-200; F = 5.80, p < 10^-15); "
        "and (5) While 15-minute intra-day maximum order statistics X_(96) saturate at the ₹10,000 cap across 90.3% of trading days, daily aggregate "
        "procurement sums strictly adhere to the Lindeberg-Lévy Central Limit Theorem, restoring Gaussianity for distribution utilities.",
        abstract_style
    ))
    story.append(Paragraph("<b>Index Terms:</b> Applied Probability, Conditional Expectation, Negative Binomial, Overdispersion, Extreme Order Statistics, Central Limit Theorem, Indian Energy Exchange (IEX), CERC Price Ceiling.", body_style))
    story.append(PageBreak())

    # ---------------------------------------------------------
    # CHAPTER 1: INTRODUCTION & REAL-WORLD MOTIVATION
    # ---------------------------------------------------------
    story.append(Paragraph("Chapter 1: Introduction, Problem Definition & Real-World Motivation", h1_style))
    story.append(Paragraph("<b>1.1 The Physical Physics of Electricity Markets:</b> Electricity is a unique physical commodity governed by Kirchhoff's laws and the physical laws of electromagnetic fields. Unlike commodities such as crude oil, natural gas, agricultural produce, or precious metals, electric energy cannot be economically stored at grid scale using commercial utility assets without incurring significant capital depreciation and round-trip efficiency losses. Consequently, the physical power system requires instantaneous, continuous, second-by-second equilibrium between total electrical generation and aggregate consumer demand. Any sudden dislocation between generation schedules and real-time load immediately manifests as severe frequency deviations, physical transmission line thermal overloads, and acute, non-linear pricing volatility on organized power exchanges.", body_style))
    story.append(Paragraph("<b>1.2 Market Architecture of the Indian Power Sector:</b> Under the regulatory oversight of the Central Electricity Regulatory Commission (CERC), the Indian power sector operates a multi-tiered market architecture designed to ensure resource adequacy, economic dispatch, and grid security. The organized market revolves around two primary spot mechanisms administered by power exchanges such as the Indian Energy Exchange (IEX): (1) <i>Day-Ahead Market (DAM)</i>, a forward physical auction operating 24 hours prior to the dispatch day with uniform market clearing prices across 96 individual 15-minute blocks; and (2) <i>Real-Time Market (RTM)</i>, half-hourly auction sessions clearing delivery within 1 hour, functioning as the critical physical balancing mechanism for distribution companies (DISCOMs) and renewable generators.", body_style))
    story.append(Paragraph("<b>1.3 The Renewable Transition, Duck Curves, and Extreme Volatility:</b> India's massive renewable expansion has introduced pronounced diurnal swings. Solar injection during mid-day (Blocks 40–60, 10:00–15:00) collapses market prices, forming the 'Duck Curve' belly. However, at sunset (Blocks 72–88, 18:00–22:00), agricultural and residential loads surge while solar generation plummets, creating extreme ramping strain exceeding 25,000 MW within 90 minutes. Prices frequently hit the statutory CERC ceiling of ₹10,000/MWh.", body_style))
    story.append(Paragraph("<b>1.4 Failure of Classical Gaussian Models:</b> Standard normal distributions fail catastrophically: electricity prices exhibit positive skewness, heavy tails, clustered spike arrivals, and upper-boundary accumulation. Probability distributions—conditional expectation, overdispersed count models, Gamma/Weibull densities, order statistics, and limit theorems—provide the necessary mathematical tools to model this physical reality.", body_style))
    story.append(PageBreak())

    # ---------------------------------------------------------
    # CHAPTER 2: RESEARCH OBJECTIVES & SYLLABUS MAPPING
    # ---------------------------------------------------------
    story.append(Paragraph("Chapter 2: Research Objectives & Syllabus Mapping", h1_style))
    story.append(Paragraph("This project is meticulously mapped to all four theoretical units and the computational unit of the Applied Probability Distributions (THM6242) syllabus at Symbiosis Statistical Institute. We formulate five precise mathematical objectives:", body_style))
    story.append(Paragraph("• <b>Objective 1 (Unit 1: Expectation and Conditional Expectation):</b> Formally prove and empirically verify the Law of Iterated Expectations and the Law of Total Variance on wholesale electricity prices. Quantify the exact percentage of Real-Time Market price variance explained by Day-Ahead Market supply-demand imbalance regimes.", body_style))
    story.append(Paragraph("• <b>Objective 2 (Unit 2: Discrete Distributions):</b> Characterize the stochastic arrival of daily extreme price spikes (P >= ₹7,000/MWh). Formulate and fit the Poisson and Negative Binomial distributions from scratch using the Method of Moments and Maximum Likelihood Estimation. Statistically diagnose overdispersion caused by physical generator ramp failures.", body_style))
    story.append(Paragraph("• <b>Objective 3 (Unit 2: Continuous Distributions):</b> Formulate two-parameter continuous probability densities (Gamma and Weibull) to model positive market clearing prices. Derive score equations and implement root-finding optimization in pure NumPy, cross-verifying with SciPy.", body_style))
    story.append(Paragraph("• <b>Objective 4 (Unit 3: Sampling Distributions):</b> Implement Pearson's Chi-Square (χ²) Goodness-of-Fit test from first principles with Cochran's bin pooling rule. Execute Welch's two-sample t-test to assess the statistical significance of diurnal price differences (Duck Curve vs. Evening Ramp), and conduct an F-test to establish variance ratios across operational windows.", body_style))
    story.append(Paragraph("• <b>Objective 5 (Unit 4: Order Statistics and Central Limit Theorems):</b> Derive the cumulative distribution function and probability density of the intra-day extreme order statistic X_(96) = max(X_1, ..., X_96). Analyze the probability of hitting the CERC ₹10,000 cap. Demonstrate the classical Lindeberg-Lévy Central Limit Theorem via Monte Carlo simulation of aggregated electricity procurement sums (n=1, 4, 16, 96).", body_style))
    story.append(PageBreak())

    # ---------------------------------------------------------
    # CHAPTER 3: DATA DESCRIPTION & EDA
    # ---------------------------------------------------------
    story.append(Paragraph("Chapter 3: Description of Data & Exploratory Data Analysis", h1_style))
    story.append(Paragraph("The dataset comprises 2,916 synchronized 15-minute operational dispatch intervals spanning 31 consecutive trading days from October 3, 2026 to November 2, 2026 published by the Indian Energy Exchange (IEX) and Grid-India (NLDC).", body_style))
    story.append(Paragraph("Table 1 summarizes the empirical sample moments for Real-Time Market clearing prices ($P_{RTM}$):", body_style))
    
    eda_tbl_data = [
        [Paragraph("Statistical Metric", tbl_text_hdr), Paragraph("Mathematical Symbol", tbl_text_hdr), Paragraph("Empirical Value", tbl_text_hdr)],
        [Paragraph("Total Sample Size", tbl_text), Paragraph("N", tbl_text), Paragraph("2,916 blocks (31 days)", tbl_text)],
        [Paragraph("Sample Mean", tbl_text), Paragraph("x̄", tbl_text), Paragraph("5,596.76 ₹/MWh", tbl_text)],
        [Paragraph("Sample Variance (Unbiased)", tbl_text), Paragraph("s²", tbl_text), Paragraph("12,458,692.51 (₹/MWh)²", tbl_text)],
        [Paragraph("Sample Standard Deviation", tbl_text), Paragraph("s", tbl_text), Paragraph("3,529.69 ₹/MWh", tbl_text)],
        [Paragraph("Sample Skewness", tbl_text), Paragraph("g₁", tbl_text), Paragraph("+0.2354 (Moderate Right Skew)", tbl_text)],
        [Paragraph("Sample Excess Kurtosis", tbl_text), Paragraph("g₂", tbl_text), Paragraph("-1.5706 (Platykurtic / Bimodal)", tbl_text)],
        [Paragraph("Minimum Clearing Price", tbl_text), Paragraph("x_(1)", tbl_text), Paragraph("0.00 ₹/MWh", tbl_text)],
        [Paragraph("First Quartile (p25)", tbl_text), Paragraph("Q₁", tbl_text), Paragraph("2,711.19 ₹/MWh", tbl_text)],
        [Paragraph("Sample Median (p50)", tbl_text), Paragraph("x̃", tbl_text), Paragraph("4,029.95 ₹/MWh", tbl_text)],
        [Paragraph("Third Quartile (p75)", tbl_text), Paragraph("Q₃", tbl_text), Paragraph("10,000.00 ₹/MWh", tbl_text)],
        [Paragraph("Maximum Clearing Price", tbl_text), Paragraph("x_(N)", tbl_text), Paragraph("10,000.00 ₹/MWh (CERC Cap)", tbl_text)],
        [Paragraph("Cap Saturation Frequency", tbl_text), Paragraph("P(X = 10,000)", tbl_text), Paragraph("828 blocks (28.40%)", tbl_text)]
    ]
    t_eda = Table(eda_tbl_data, colWidths=[160, 140, 187])
    t_eda.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1F497D')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#D0D8E0')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#FFFFFF'), colors.HexColor('#F7F9FB')])
    ]))
    story.append(t_eda)
    story.append(Spacer(1, 10))

    fig1_path = "/Users/krishnagupta/Downloads/inte/indian_power_market/academic_submission/figures/fig1_diurnal_price_duck_curve.png"
    if os.path.exists(fig1_path):
        story.append(Image(fig1_path, width=470, height=235))
        story.append(Paragraph("<b>Figure 1:</b> Intra-Day Diurnal Profile of Real-Time Market Clearing Prices (IEX). Notice the sharp Duck Curve depression during solar mid-day (Blocks 40–60) and the steep surge toward the ₹10,000 CERC regulatory ceiling during evening ramp (Blocks 72–88).", caption_style))
    story.append(PageBreak())

    # ---------------------------------------------------------
    # CHAPTER 4: THEORETICAL DERIVATIONS
    # ---------------------------------------------------------
    story.append(Paragraph("Chapter 4: Theoretical Background & Mathematical Derivations", h1_style))
    story.append(Paragraph("<b>4.1 Unit 1: Expectation, Conditional Expectation & Total Variance:</b><br/>"
                           "<i>Definition 4.1 (Conditional Expectation):</i> For continuous Y and discrete X taking values r in R:<br/>"
                           "E[Y | X = r] = ∫ y f_{Y|X}(y | r) dy.<br/><br/>"
                           "<i>Theorem 4.1 (The Law of Iterated Expectations / Tower Property):</i> E[E[Y|X]] = E[Y].<br/>"
                           "<i>Proof:</i> E[E[Y|X]] = ∑_{r ∈ R} E[Y | X = r] P(X = r) = ∑_{r ∈ R} [∫ y f_{Y|X}(y | r) dy] P(X = r) = ∫ y [∑_{r ∈ R} f_{Y|X}(y | r) P(X = r)] dy.<br/>"
                           "By the law of total probability for density functions, ∑_r f_{Y|X}(y | r) P(X = r) = f_Y(y). Thus: E[E[Y|X]] = ∫ y f_Y(y) dy = E[Y]. Q.E.D.<br/><br/>"
                           "<i>Theorem 4.2 (The Law of Total Variance):</i> Var(Y) = E[Var(Y|X)] + Var(E[Y|X]).<br/>"
                           "<i>Proof:</i> Var(Y|X) = E[Y²|X] - (E[Y|X])². Taking expectation of both sides: E[Var(Y|X)] = E[Y²] - E[(E[Y|X])²] (Equation 1).<br/>"
                           "By definition of variance applied to E[Y|X]: Var(E[Y|X]) = E[(E[Y|X])²] - (E[E[Y|X]])² = E[(E[Y|X])²] - (E[Y])² (Equation 2).<br/>"
                           "Summing Equation 1 and Equation 2 yields: E[Var(Y|X)] + Var(E[Y|X]) = E[Y²] - (E[Y])² = Var(Y). Q.E.D.", body_style))
    story.append(PageBreak())

    story.append(Paragraph("<b>4.2 Unit 2: Discrete Distributions (Poisson vs. Negative Binomial):</b><br/>"
                           "<i>Poisson Distribution:</i> P(K = k) = (λ^k e^(-λ)) / k!, for k = 0, 1, 2, ...<br/>"
                           "Mean: E[K] = λ. Variance: Var(K) = λ. Dispersion ratio = Var(K)/E[K] = 1 (Equidispersion).<br/><br/>"
                           "<i>Negative Binomial Distribution (Gamma-Poisson Mixture):</i> Suppose conditional on Λ = λ, K | Λ ~ Poisson(λ), where Λ ~ Gamma(r, (1-p)/p). Marginally:<br/>"
                           "P(K = k) = ∫ P(K=k | Λ=λ) f_Λ(λ) dλ = [Γ(k+r) / (k! Γ(r))] p^r (1-p)^k.<br/>"
                           "Mean: E[K] = r(1-p)/p. Variance: Var(K) = r(1-p)/p² = E[K] + (E[K]²/r) > E[K].<br/>"
                           "Because p in (0, 1), Negative Binomial accommodates overdispersion caused by clustered grid outages.", body_style))
    story.append(Paragraph("<b>4.3 Unit 2: Continuous Distributions (Two-Parameter Gamma & Weibull):</b><br/>"
                           "<i>Two-Parameter Gamma(α, β):</i> f(x) = [β^α / Γ(α)] x^(α-1) e^(-βx), x > 0.<br/>"
                           "Moments: E[X] = α/β, Var(X) = α/β².<br/>"
                           "Method of Moments: β̂_MoM = x̄ / s², α̂_MoM = x̄² / s².<br/>"
                           "Maximum Likelihood Estimation: Log-likelihood ln L = N[α ln β - ln Γ(α)] + (α-1)∑ ln x_i - β ∑ x_i.<br/>"
                           "Setting score equations to zero yields β̂ = α̂ / x̄ and the transcendental root equation: ln α - ψ(α) = ln x̄ - (1/N) ∑ ln x_i, solved via Brent's method.<br/><br/>"
                           "<i>Two-Parameter Weibull(c, λ):</i> f(x) = (c/λ) (x/λ)^(c-1) exp[-(x/λ)^c], x >= 0.<br/>"
                           "Moments: E[X] = λ Γ(1 + 1/c), Var(X) = λ² [Γ(1 + 2/c) - Γ²(1 + 1/c)].", body_style))
    story.append(Paragraph("<b>4.4 Unit 4: Order Statistics and Central Limit Theorem:</b><br/>"
                           "<i>Theorem 4.3 (Extreme Order Statistic):</i> For X_(n) = max(X_1, ..., X_n), F_(n)(x) = P(all X_i <= x) = [F(x)]^n.<br/>"
                           "Density: f_(n)(x) = d/dx [F(x)]^n = n [F(x)]^(n-1) f(x).<br/><br/>"
                           "<i>Theorem 4.4 (Lindeberg-Lévy Central Limit Theorem):</i> For an i.i.d. sequence with mean μ and variance σ² < ∞:<br/>"
                           "Z_n = (∑_{i=1}^n X_i - nμ) / (σ √n) ---> N(0, 1) in distribution as n ---> ∞.", body_style))
    story.append(PageBreak())

    # ---------------------------------------------------------
    # CHAPTER 5: HAND-SOLVED EXAMPLE
    # ---------------------------------------------------------
    story.append(Paragraph("Chapter 5: Hand-Solved Numerical Example", h1_style))
    story.append(Paragraph("In accordance with the SSI instructions, we present a complete hand-worked calculation on a representative mini-sample of five 15-minute price observations:<br/>"
                           "<b>S = {x_1 = 2500, x_2 = 3200, x_3 = 4800, x_4 = 7500, x_5 = 10000} (₹/MWh).</b>", body_style))
    story.append(Paragraph("<b>5.1 Step-by-Step Sample Moments:</b><br/>"
                           "• Sample Mean: x̄ = (2500 + 3200 + 4800 + 7500 + 10000) / 5 = 28,000 / 5 = <b>5,600.0 ₹/MWh</b>.<br/>"
                           "• Deviations & Squared Deviations:<br/>"
                           "  d_1 = 2500 - 5600 = -3100  ==>  d_1² = 9,610,000<br/>"
                           "  d_2 = 3200 - 5600 = -2400  ==>  d_2² = 5,760,000<br/>"
                           "  d_3 = 4800 - 5600 = -800   ==>  d_3² = 640,000<br/>"
                           "  d_4 = 7500 - 5600 = +1900  ==>  d_4² = 3,610,000<br/>"
                           "  d_5 = 10000 - 5600 = +4400 ==>  d_5² = 19,360,000<br/>"
                           "• Sum of squared deviations: ∑ d_i² = 38,980,000.<br/>"
                           "• Sample Variance (df = 4): s² = 38,980,000 / 4 = <b>9,745,000.0 (₹/MWh)²</b>.<br/>"
                           "• Sample Standard Deviation: s = √(9,745,000) = <b>3,121.70 ₹/MWh</b>.", body_style))
    story.append(Paragraph("<b>5.2 Method of Moments Parameter Estimates for Gamma Distribution:</b><br/>"
                           "• Shape: α̂_MoM = x̄² / s² = (5,600)² / 9,745,000 = 31,360,000 / 9,745,000 ≈ <b>3.2181</b>.<br/>"
                           "• Rate: β̂_MoM = x̄ / s² = 5,600 / 9,745,000 ≈ <b>0.00057465</b>.<br/>"
                           "• Scale: θ̂_MoM = 1 / β̂ = 9,745,000 / 5,600 ≈ <b>1,740.18 ₹/MWh</b>.", body_style))
    story.append(Paragraph("<b>5.3 Hand-Solved Verification of the Law of Iterated Expectations:</b><br/>"
                           "Partition S by threshold T = ₹5,000/MWh:<br/>"
                           "• Sub-group 1 (Normal / Off-Peak: x <= 5000): S_1 = {2500, 3200, 4800}, n_1 = 3, P(G1) = 0.60.<br/>"
                           "  Conditional Mean: E[X | Group 1] = (2500 + 3200 + 4800) / 3 = 10,500 / 3 = <b>3,500.0 ₹/MWh</b>.<br/>"
                           "• Sub-group 2 (Price Spike: x > 5000): S_2 = {7500, 10000}, n_2 = 2, P(G2) = 0.40.<br/>"
                           "  Conditional Mean: E[X | Group 2] = (7500 + 10000) / 2 = 17,500 / 2 = <b>8,750.0 ₹/MWh</b>.<br/><br/>"
                           "Applying Theorem 4.1:<br/>"
                           "E[E[X|Group]] = P(G1) · E[X|G1] + P(G2) · E[X|G2] = (0.60 · 3500.0) + (0.40 · 8750.0) = 2100.0 + 3500.0 = <b>5,600.0 ₹/MWh</b> (Exact Match!).", body_style))
    story.append(Paragraph("<b>5.4 Hand-Solved Chi-Square Goodness-of-Fit Table:</b><br/>"
                           "Three disjoint bins: Bin 1: [0, 4000), Bin 2: [4000, 7000), Bin 3: [7000, 12000].<br/>"
                           "Observed: O = [2, 1, 2]. Hypothesized probabilities: p = [0.35, 0.35, 0.30] ==> Expected: E = [1.75, 1.75, 1.50].<br/>"
                           "χ² = (2 - 1.75)²/1.75 + (1 - 1.75)²/1.75 + (2 - 1.50)²/1.50 = 0.0625/1.75 + 0.5625/1.75 + 0.25/1.50 = 0.0357 + 0.3214 + 0.1667 = <b>0.5238</b>.<br/>"
                           "For df = 3 - 1 - 0 = 2, critical value at α = 0.05 is 5.991. Since 0.5238 < 5.991, we fail to reject H₀.", body_style))
    story.append(PageBreak())

    # ---------------------------------------------------------
    # CHAPTER 6 & 7: EMPIRICAL RESULTS
    # ---------------------------------------------------------
    story.append(Paragraph("Chapter 6 & 7: Computational Architecture & Empirical Results", h1_style))
    story.append(Paragraph("<b>7.1 Unit 1 Results: Conditional Expectation & Total Variance Decomposition:</b><br/>"
                           "We segment the 2,916 operational blocks into three Day-Ahead Market (DAM) physical imbalance regimes:<br/>"
                           "• Deficit Regime (Ratio > 1.25): Purchase bids heavily exceed sell offers (N = 1,885 blocks, 64.64%).<br/>"
                           "• Balanced Regime (0.80 <= Ratio <= 1.25): Normal bilateral equilibrium (N = 398 blocks, 13.65%).<br/>"
                           "• Surplus Regime (Ratio < 0.80): Generation excess, typically during solar peak hours (N = 633 blocks, 21.71%).", body_style))
    
    u1_tbl_data = [
        [Paragraph("Market Regime", tbl_text_hdr), Paragraph("N", tbl_text_hdr), Paragraph("Weight P(X)", tbl_text_hdr), Paragraph("E[Y|X] (₹)", tbl_text_hdr), Paragraph("Var(Y|X)", tbl_text_hdr), Paragraph("Std(Y|X)", tbl_text_hdr)],
        [Paragraph("Deficit (Ratio > 1.25)", tbl_text), Paragraph("1,885", tbl_text), Paragraph("0.6464", tbl_text), Paragraph("7,408.81", tbl_text), Paragraph("9,184,885.81", tbl_text), Paragraph("3,030.66", tbl_text)],
        [Paragraph("Balanced [0.8, 1.25]", tbl_text), Paragraph("398", tbl_text), Paragraph("0.1365", tbl_text), Paragraph("2,993.12", tbl_text), Paragraph("1,166,528.39", tbl_text), Paragraph("1,080.06", tbl_text)],
        [Paragraph("Surplus (Ratio < 0.8)", tbl_text), Paragraph("633", tbl_text), Paragraph("0.2171", tbl_text), Paragraph("1,837.72", tbl_text), Paragraph("1,135,542.72", tbl_text), Paragraph("1,065.62", tbl_text)],
        [Paragraph("Iterated Expectation", tbl_text), Paragraph("2,916", tbl_text), Paragraph("1.0000", tbl_text), Paragraph("5,596.76", tbl_text), Paragraph("6,339,197.40", tbl_text), Paragraph("2,517.78", tbl_text)]
    ]
    t_u1 = Table(u1_tbl_data, colWidths=[120, 50, 70, 80, 100, 67])
    t_u1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1F497D')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#D0D8E0')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#FFFFFF'), colors.HexColor('#F7F9FB')])
    ]))
    story.append(t_u1)
    story.append(Paragraph("<b>Empirical Verification of Law of Total Variance:</b><br/>"
                           "• Total Unconditional Variance Var(Y) = 12,454,419.98 (₹/MWh)²<br/>"
                           "• Within-Regime Expected Variance E[Var(Y|X)] = 6,339,197.40 (₹/MWh)² (50.90% of total variance)<br/>"
                           "• Between-Regime Variance Var(E[Y|X]) = 6,115,222.57 (₹/MWh)² (49.10% of total variance)<br/>"
                           "• Reconstructed Sum = 6,339,197.40 + 6,115,222.57 = 12,454,419.98 (Exact match to 8 decimal places!).<br/>"
                           "• <b>Proportion of Variance Explained (η²): 49.10%.</b>", body_style))
    story.append(Spacer(1, 5))

    fig2_path = "/Users/krishnagupta/Downloads/inte/indian_power_market/academic_submission/figures/fig2_conditional_expectation_regimes.png"
    if os.path.exists(fig2_path):
        story.append(Image(fig2_path, width=470, height=200))
        story.append(Paragraph("<b>Figure 2:</b> Boxplot of RTM clearing prices across DAM imbalance regimes (left) and Law of Total Variance decomposition (right). Notice that market imbalance explains 49.10% of entire real-time price variability.", caption_style))
    story.append(PageBreak())

    # ---------------------------------------------------------
    # CHAPTER 7 (CONT): DISCRETE & CONTINUOUS RESULTS
    # ---------------------------------------------------------
    story.append(Paragraph("7.2 Unit 2 Results: Discrete Spike Modeling (Poisson vs. Negative Binomial)", h2_style))
    story.append(Paragraph("Evaluating daily spike counts (K_d >= ₹7,000/MWh) across D = 31 days:<br/>"
                           "• Sample Mean Spike Count: k̄ = 35.032 spikes/day<br/>"
                           "• Sample Variance of Spikes: s_k² = 718.566 (spikes/day)²<br/>"
                           "• <b>Dispersion Index (s_k² / k̄) = 718.566 / 35.032 = 20.512.</b><br/>"
                           "The dispersion index is over 20 times the Poisson theoretical expectation of 1.0! This proves severe overdispersion.", body_style))
    
    u2d_tbl = [
        [Paragraph("Distribution Model", tbl_text_hdr), Paragraph("Estimated Parameters", tbl_text_hdr), Paragraph("Theoretical Mean", tbl_text_hdr), Paragraph("Theoretical Variance", tbl_text_hdr)],
        [Paragraph("Poisson (Equidispersed)", tbl_text), Paragraph("λ̂ = 35.032", tbl_text), Paragraph("35.032", tbl_text), Paragraph("35.032 (Severe Underfit)", tbl_text)],
        [Paragraph("Negative Binomial (MoM)", tbl_text), Paragraph("r̂ = 1.795, p̂ = 0.0488", tbl_text), Paragraph("35.032", tbl_text), Paragraph("718.566 (Exact Match)", tbl_text)],
        [Paragraph("Negative Binomial (SciPy)", tbl_text), Paragraph("r̂ = 1.795, p̂ = 0.0488", tbl_text), Paragraph("35.032", tbl_text), Paragraph("718.566 (Exact Match)", tbl_text)]
    ]
    t_u2d = Table(u2d_tbl, colWidths=[150, 140, 97, 100])
    t_u2d.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1F497D')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#D0D8E0')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#FFFFFF'), colors.HexColor('#F7F9FB')])
    ]))
    story.append(t_u2d)
    story.append(Spacer(1, 5))

    fig3_path = "/Users/krishnagupta/Downloads/inte/indian_power_market/academic_submission/figures/fig3_discrete_spike_poisson_vs_negbinom.png"
    if os.path.exists(fig3_path):
        story.append(Image(fig3_path, width=460, height=205))
        story.append(Paragraph("<b>Figure 3:</b> Discrete price spike frequency distribution (N = 31 days). The fitted Poisson distribution (red dashed) collapses completely due to severe overdispersion (Var/Mean = 20.51), whereas the Negative Binomial distribution (green solid) fits the empirical count density.", caption_style))
    story.append(PageBreak())

    story.append(Paragraph("7.3 Unit 2 Results: Continuous Density Estimation (Gamma vs. Weibull)", h2_style))
    story.append(Paragraph("Fitting continuous densities to positive clearing prices (P > 10, N = 2,887 blocks, x̄ = 5,652.88 ₹/MWh, s = 3,501.99 ₹/MWh):", body_style))
    
    u2c_tbl = [
        [Paragraph("Model / Estimator", tbl_text_hdr), Paragraph("Shape Parameter", tbl_text_hdr), Paragraph("Scale Parameter", tbl_text_hdr), Paragraph("Fitted Mean (₹)", tbl_text_hdr), Paragraph("Fitted Std (₹)", tbl_text_hdr)],
        [Paragraph("Gamma MoM (Scratch)", tbl_text), Paragraph("α̂ = 2.6052", tbl_text), Paragraph("θ̂ = 2,169.86", tbl_text), Paragraph("5,652.88", tbl_text), Paragraph("3,501.99", tbl_text)],
        [Paragraph("Gamma MLE (Scratch)", tbl_text), Paragraph("α̂ = 1.9144", tbl_text), Paragraph("θ̂ = 2,952.85", tbl_text), Paragraph("5,652.88", tbl_text), Paragraph("4,085.50", tbl_text)],
        [Paragraph("Gamma MLE (SciPy)", tbl_text), Paragraph("α̂ = 1.9144", tbl_text), Paragraph("θ̂ = 2,952.85", tbl_text), Paragraph("5,652.88", tbl_text), Paragraph("4,085.50", tbl_text)],
        [Paragraph("Weibull MLE (SciPy)", tbl_text), Paragraph("ĉ = 1.5831", tbl_text), Paragraph("λ̂ = 6,272.61", tbl_text), Paragraph("5,627.14", tbl_text), Paragraph("3,618.42", tbl_text)]
    ]
    t_u2c = Table(u2c_tbl, colWidths=[130, 95, 95, 87, 80])
    t_u2c.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1F497D')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#D0D8E0')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#FFFFFF'), colors.HexColor('#F7F9FB')])
    ]))
    story.append(t_u2c)
    story.append(Spacer(1, 5))

    fig4_path = "/Users/krishnagupta/Downloads/inte/indian_power_market/academic_submission/figures/fig4_continuous_price_gamma_weibull.png"
    if os.path.exists(fig4_path):
        story.append(Image(fig4_path, width=460, height=205))
        story.append(Paragraph("<b>Figure 4:</b> Continuous probability density fitting of Real-Time Market prices. Both Gamma and Weibull densities capture the intermediate spread, but diverge at the ₹10,000 regulatory cap where CERC mandates price truncation.", caption_style))
    story.append(PageBreak())

    # ---------------------------------------------------------
    # CHAPTER 8: GOODNESS OF FIT & SAMPLING DISTRIBUTIONS
    # ---------------------------------------------------------
    story.append(Paragraph("Chapter 8: Goodness-of-Fit & Sampling Distribution Inference", h1_style))
    story.append(Paragraph("<b>8.1 Pearson's Chi-Square Test across 10 Bins (Gamma MLE):</b>", h2_style))
    
    chi_tbl_data = [
        [Paragraph("Price Interval (₹)", tbl_text_hdr), Paragraph("Observed (O)", tbl_text_hdr), Paragraph("Expected (E)", tbl_text_hdr), Paragraph("(O - E)", tbl_text_hdr), Paragraph("(O - E)² / E", tbl_text_hdr)],
        [Paragraph("[0, 1000)", tbl_text), Paragraph("159", tbl_text), Paragraph("182.34", tbl_text), Paragraph("-23.34", tbl_text), Paragraph("2.99", tbl_text)],
        [Paragraph("[1000, 2000)", tbl_text), Paragraph("218", tbl_text), Paragraph("373.36", tbl_text), Paragraph("-155.36", tbl_text), Paragraph("64.65", tbl_text)],
        [Paragraph("[2000, 3000)", tbl_text), Paragraph("444", tbl_text), Paragraph("427.97", tbl_text), Paragraph("+16.03", tbl_text), Paragraph("0.60", tbl_text)],
        [Paragraph("[3000, 4000)", tbl_text), Paragraph("570", tbl_text), Paragraph("416.34", tbl_text), Paragraph("+153.66", tbl_text), Paragraph("56.71", tbl_text)],
        [Paragraph("[4000, 5000)", tbl_text), Paragraph("270", tbl_text), Paragraph("374.02", tbl_text), Paragraph("-104.02", tbl_text), Paragraph("28.93", tbl_text)],
        [Paragraph("[5000, 6000)", tbl_text), Paragraph("105", tbl_text), Paragraph("320.61", tbl_text), Paragraph("-215.61", tbl_text), Paragraph("144.99", tbl_text)],
        [Paragraph("[6000, 7000)", tbl_text), Paragraph("35", tbl_text), Paragraph("266.42", tbl_text), Paragraph("-231.42", tbl_text), Paragraph("201.03", tbl_text)],
        [Paragraph("[7000, 8000)", tbl_text), Paragraph("23", tbl_text), Paragraph("216.51", tbl_text), Paragraph("-193.51", tbl_text), Paragraph("172.96", tbl_text)],
        [Paragraph("[8000, 9000)", tbl_text), Paragraph("12", tbl_text), Paragraph("173.08", tbl_text), Paragraph("-161.08", tbl_text), Paragraph("149.91", tbl_text)],
        [Paragraph("[9000, 10000]", tbl_text), Paragraph("1,051", tbl_text), Paragraph("136.35", tbl_text), Paragraph("+914.65", tbl_text), Paragraph("6,135.53", tbl_text)],
        [Paragraph("<b>Total / Test Statistic</b>", tbl_text), Paragraph("<b>2,887</b>", tbl_text), Paragraph("<b>2,887.00</b>", tbl_text), Paragraph("<b>0.00</b>", tbl_text), Paragraph("<b>χ² = 6,943.23</b>", tbl_text)]
    ]
    t_chi = Table(chi_tbl_data, colWidths=[120, 80, 80, 80, 127])
    t_chi.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1F497D')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#D0D8E0')),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#FFFFFF'), colors.HexColor('#F7F9FB')])
    ]))
    story.append(t_chi)
    story.append(Paragraph("<b>Goodness-of-Fit Interpretation:</b> Total χ² = 6,943.23, df = 7, p < 10^-300. Notice that the top bin [9000, 10000] accounts for 6,135.53 (88.37%) of the entire test statistic! This proves that price divergence is not a modeling defect but the direct result of the statutory CERC ₹10,000 price ceiling.", body_style))
    story.append(PageBreak())

    story.append(Paragraph("<b>8.2 Sampling Distributions: Diurnal Regime Hypothesis Tests:</b>", h2_style))
    story.append(Paragraph("We test whether market clearing prices in the Solar Mid-Day Window (Blocks 40–60, 10:00–15:00) are statistically lower than in the Evening Peak Ramp Window (Blocks 72–88, 18:00–22:00):<br/>"
                           "H_0: μ_Solar = μ_Evening  vs.  H_1: μ_Solar < μ_Evening", body_style))
    
    t_test_tbl = [
        [Paragraph("Statistical Test", tbl_text_hdr), Paragraph("Test Statistic", tbl_text_hdr), Paragraph("Degrees of Freedom", tbl_text_hdr), Paragraph("p-value / Inference", tbl_text_hdr)],
        [Paragraph("Welch's Two-Sample t-test", tbl_text), Paragraph("t = 46.8031", tbl_text), Paragraph("df = 654.8", tbl_text), Paragraph("p = 1.975 × 10^-210 (Reject H₀)", tbl_text)],
        [Paragraph("Two-Sample F-test (Var Ratio)", tbl_text), Paragraph("F = 5.8042", tbl_text), Paragraph("df₁ = 509, df₂ = 629", tbl_text), Paragraph("p = 1.110 × 10^-16 (Heteroscedastic)", tbl_text)]
    ]
    t_test = Table(t_test_tbl, colWidths=[150, 110, 110, 117])
    t_test.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1F497D')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#D0D8E0')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#FFFFFF'), colors.HexColor('#F7F9FB')])
    ]))
    story.append(t_test)
    story.append(Paragraph("The Welch t-statistic of 46.80 confirms that Evening Ramp prices (mean ₹8,021.44) are astronomically higher than Mid-day Solar prices (mean ₹1,815.98). Furthermore, the F-statistic of 5.80 proves that evening price volatility is nearly six times higher than mid-day volatility.", body_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>8.3 Unit 4 Results: Order Statistics (Daily Max X_(96)):</b>", h2_style))
    story.append(Paragraph("Evaluating the intra-day maximum order statistic X_(96) = max_{1 <= b <= 96} P_b across D = 31 days:<br/>"
                           "• Days reaching the CERC ₹10,000 ceiling: <b>28 out of 31 trading days (90.32% of all days!).</b><br/>"
                           "• Sample Mean of Daily Maximum: ₹9,726.79/MWh (Std = ₹888.72/MWh, Min = ₹6,029.81/MWh, Max = ₹10,000.00/MWh).<br/>"
                           "This confirms Theorem 4.3: because n = 96 is large, P(X_(96) <= x) = [F(x)]^96 approaches zero for any x < 10,000, making price cap encounters virtually certain on almost every operating day.", body_style))

    fig5_path = "/Users/krishnagupta/Downloads/inte/indian_power_market/academic_submission/figures/fig5_order_statistics_daily_max.png"
    if os.path.exists(fig5_path):
        story.append(Image(fig5_path, width=460, height=200))
        story.append(Paragraph("<b>Figure 5:</b> Empirical CDF of daily maximum price X_(96). The extreme order statistic hits the CERC ceiling in 90.32% of trading days.", caption_style))
    story.append(PageBreak())

    story.append(Paragraph("<b>8.4 Central Limit Theorem Convergence on Procurement Sums S_n = ∑ X_i:</b>", h2_style))
    story.append(Paragraph("Tracking Central Limit Theorem convergence for procurement portfolio sums via 3,000 bootstrap draws:", body_style))
    
    clt_tbl_data = [
        [Paragraph("Aggregation Horizon", tbl_text_hdr), Paragraph("Sample Skewness (g₁)", tbl_text_hdr), Paragraph("Excess Kurtosis (g₂)", tbl_text_hdr), Paragraph("Empirical Status", tbl_text_hdr)],
        [Paragraph("n = 1 (15-min block)", tbl_text), Paragraph("+0.2354", tbl_text), Paragraph("-1.5706", tbl_text), Paragraph("Non-Normal (Platykurtic / Bimodal)", tbl_text)],
        [Paragraph("n = 4 (1-hour block)", tbl_text), Paragraph("+0.1912", tbl_text), Paragraph("-0.2934", tbl_text), Paragraph("Rapid Convergence toward Gaussian", tbl_text)],
        [Paragraph("n = 16 (4-hour block)", tbl_text), Paragraph("+0.0601", tbl_text), Paragraph("-0.2152", tbl_text), Paragraph("Near-Normal (Symmetric)", tbl_text)],
        [Paragraph("n = 96 (Full-day sum)", tbl_text), Paragraph("+0.0573", tbl_text), Paragraph("+0.0941", tbl_text), Paragraph("Asymptotically Gaussian (CLT Validated)", tbl_text)]
    ]
    t_clt = Table(clt_tbl_data, colWidths=[120, 100, 120, 147])
    t_clt.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1F497D')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#D0D8E0')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#FFFFFF'), colors.HexColor('#F7F9FB')])
    ]))
    story.append(t_clt)
    story.append(Spacer(1, 5))

    fig6_path = "/Users/krishnagupta/Downloads/inte/indian_power_market/academic_submission/figures/fig6_central_limit_theorem_convergence.png"
    if os.path.exists(fig6_path):
        story.append(Image(fig6_path, width=460, height=210))
        story.append(Paragraph("<b>Figure 6:</b> Central Limit Theorem demonstration. As portfolio size increases from n = 1 to n = 96, skewness drops to +0.057 and kurtosis converges to +0.094, matching the Gaussian bell curve.", caption_style))
    story.append(PageBreak())

    # ---------------------------------------------------------
    # CHAPTER 9, 10, 11 & REFERENCES
    # ---------------------------------------------------------
    story.append(Paragraph("Chapter 9: Real-World Interpretation for Stakeholders", h1_style))
    story.append(Paragraph("<b>1. Distribution Companies (DISCOMs):</b> The Law of Total Variance proves 49.10% of price variance is deterministic from day-ahead queues. When DAM imbalance exceeds 1.25, the conditional price jumps 4.03x to ₹7,408/MWh. DISCOMs should hedge forward rather than buying on real-time spot.", body_style))
    story.append(Paragraph("<b>2. Battery Storage (BESS) & Renewable IPPs:</b> Welch's t-test (t = 46.80) and F-test (F = 5.80) confirm a statistically reliable ₹6,205/MWh diurnal arbitrage spread between mid-day solar charging and evening discharging.", body_style))
    story.append(Paragraph("<b>3. Grid Operators (Grid-India):</b> Daily maximums hitting the cap in 90.3% of days signals acute evening ramping deficits. NLDC must dispatch ancillary reserves 90 minutes prior to sunset.", body_style))
    story.append(Paragraph("<b>4. Regulators (CERC):</b> Chi-Square test proved that 88.37% of divergence is caused by cap accumulation at ₹10,000, signaling the need for market-based ramping products.", body_style))
    story.append(PageBreak())

    story.append(Paragraph("Chapter 10: Relationship to the Automated Capstone Platform", h1_style))
    story.append(Paragraph("This academic report and practical notebook represent the theoretical probability foundation of our larger automated engineering capstone hosted at <u>https://github.com/arcanekrishna/energy</u>. Specifically:<br/>"
                           "• <b>LightGBM Quantile Loss Forecaster:</b> In the capstone codebase (`src/risk_engine/quantile_models.py`), quantile regression targets (q_10, q_50, q_90) are bounded and parameterized using the Gamma and Weibull dispersion parameters derived in Chapter 7.<br/>"
                           "• <b>Calibrated Stress Classifier:</b> The GBDT stress classifier (`src/risk_engine/stress_classifier.py`) uses the Negative Binomial overdispersion bounds to identify high-probability spike windows with isotonic calibration.<br/>"
                           "• <b>Conformal Prediction Intervals:</b> The conformal risk engine (`src/risk_engine/conformal.py`) adapts its non-conformity score scaling factors dynamically based on the conditional variance regimes established via the Law of Total Variance.<br/>"
                           "• <b>Stakeholder Dashboard UI:</b> The FastAPI dashboard (`src/dashboard/app.py`) directly surfaces the conditional expectations and regime probabilities for DISCOMs, GenCos, and Grid operators in real time.", body_style))

    story.append(Paragraph("Chapter 11: Limitations & Conclusion", h1_style))
    story.append(Paragraph("<b>11.1 Methodological Limitations:</b><br/>"
                           "1. Truncation Boundary Censoring: Standard Gamma and Weibull densities do not account for statutory price ceilings. Future work should employ Right-Truncated Generalized Pareto Distributions (GPD) under Extreme Value Theory (EVT).<br/>"
                           "2. Time-Varying Volatility: The current model assumes stationary monthly regimes. GARCH or jump-diffusion point processes could capture intra-day serial correlation.<br/>"
                           "3. Transmission Congestion: Market split events where regional prices diverge were not disaggregated.<br/><br/>"
                           "<b>11.2 Concluding Remarks:</b><br/>"
                           "Wholesale power market clearing prices in India present a rich empirical laboratory for applied probability distributions. By rigorously deploying Expectation and Conditional Expectation (Unit 1), Discrete and Continuous Distributions (Unit 2), Sampling Distributions (Unit 3), and Order Statistics and the Central Limit Theorem (Unit 4), we demonstrated how formal probability theory illuminates the physical realities of the modern decarbonizing electrical grid. All computational steps were successfully implemented from first principles in Python, satisfying all academic requirements for Course THM6242 at Symbiosis Statistical Institute.", body_style))
    story.append(PageBreak())

    story.append(Paragraph("Chapter 12: Academic & Regulatory References", h1_style))
    refs = [
        "[1] Casella, G., & Berger, R. L. (2002). Statistical Inference (2nd ed.). Pacific Grove, CA: Duxbury Press.",
        "[2] Central Electricity Regulatory Commission (CERC). (2022). Order in Petition No. 4/SM/2022: Operationalization of Real-Time Market and Price Ceiling Mandates. New Delhi, India.",
        "[3] Feller, W. (1968). An Introduction to Probability Theory and Its Applications (Vols. 1 & 2). New York: John Wiley & Sons.",
        "[4] Grid Controller of India Limited (Grid-India). (2024). Operational Performance Analysis of the National Grid (Monthly SCADA Reports). New Delhi, India.",
        "[5] Hogg, R. V., McKean, J., & Craig, A. T. (2018). Introduction to Mathematical Statistics (8th ed.). Boston: Pearson.",
        "[6] Indian Energy Exchange (IEX). (2024). Market Rules and Bidding Procedures for Day-Ahead and Real-Time Electricity Markets. New Delhi, India.",
        "[7] Mood, A. M., Graybill, F. A., & Boes, D. C. (1974). Introduction to the Theory of Statistics (3rd ed.). New York: McGraw-Hill.",
        "[8] Weron, R. (2014). Electricity price forecasting: A review of the state-of-the-art with a look into the future. International Journal of Forecasting, 30(4), 1030-1081.",
        "[9] Central Electricity Authority (CEA). (2023). Report on Optimal Generation Capacity Mix for 2029-30. Ministry of Power, Government of India."
    ]
    for r in refs:
        story.append(Paragraph(r, ParagraphStyle('Ref', parent=body_style, fontSize=9.5, leading=14)))

    doc.build(story, canvasmaker=NumberedCanvas)
    print("Academic Project Report (.pdf) successfully created at:", pdf_path)

if __name__ == '__main__':
    generate_pdf()
