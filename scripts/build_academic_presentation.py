import os
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

    # Color Palette: Executive Navy, Slate, & Energy Orange
    c_navy = RGBColor(11, 37, 89)        # #0B2559
    c_blue = RGBColor(25, 75, 145)       # #194B91
    c_light_bg = RGBColor(245, 248, 252) # #F5F8FC
    c_card_bg = RGBColor(255, 255, 255)
    c_accent = RGBColor(230, 81, 0)      # #E65100
    c_teal = RGBColor(0, 105, 92)        # #00695C
    c_dark = RGBColor(33, 37, 41)        # #212529
    c_white = RGBColor(255, 255, 255)
    c_gray = RGBColor(100, 110, 125)
    c_border = RGBColor(210, 220, 235)

    base_dir = "/Users/krishnagupta/Downloads/inte/indian_power_market"
    fig_dir = os.path.join(base_dir, "academic_submission", "figures")
    nb_fig_dir = os.path.join(fig_dir, "notebook_extracted")
    out_pptx = os.path.join(base_dir, "academic_submission", "presentation", "Group05_Title05_Presentation.pptx")

    def set_bg(slide, color=c_light_bg):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = color
        bg.line.color.rgb = color

    def add_header(slide, title_text, category_text="SYMBIOSIS STATISTICAL INSTITUTE | THM6242: APPLIED PROBABILITY DISTRIBUTIONS", slide_num=None):
        set_bg(slide, c_light_bg)
        banner = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(1.08))
        banner.fill.solid()
        banner.fill.fore_color.rgb = c_navy
        banner.line.color.rgb = c_navy

        tx_box = slide.shapes.add_textbox(Inches(0.65), Inches(0.10), Inches(12.0), Inches(0.9))
        tf = tx_box.text_frame
        tf.word_wrap = True
        p_cat = tf.paragraphs[0]
        p_cat.text = category_text.upper()
        p_cat.font.name = "Calibri"
        p_cat.font.size = Pt(10)
        p_cat.font.bold = True
        p_cat.font.color.rgb = RGBColor(175, 200, 240)

        p_title = tf.add_paragraph()
        p_title.text = title_text
        p_title.font.name = "Calibri"
        p_title.font.size = Pt(21)
        p_title.font.bold = True
        p_title.font.color.rgb = c_white

        accent_line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(1.06), Inches(13.333), Inches(0.05))
        accent_line.fill.solid()
        accent_line.fill.fore_color.rgb = c_accent
        accent_line.line.color.rgb = c_accent

        # Footer
        footer_box = slide.shapes.add_textbox(Inches(0.65), Inches(7.12), Inches(10.0), Inches(0.3))
        tf_f = footer_box.text_frame
        p_f = tf_f.paragraphs[0]
        p_f.text = "Indian Electricity Market (IEX) Stochastic Modeling | Group 05"
        p_f.font.name = "Calibri"
        p_f.font.size = Pt(10)
        p_f.font.color.rgb = c_gray

        if slide_num is not None:
            num_box = slide.shapes.add_textbox(Inches(11.8), Inches(7.12), Inches(0.9), Inches(0.3))
            tf_n = num_box.text_frame
            p_n = tf_n.paragraphs[0]
            p_n.alignment = PP_ALIGN.RIGHT
            p_n.text = f"{slide_num} / 15"
            p_n.font.name = "Calibri"
            p_n.font.size = Pt(10)
            p_n.font.bold = True
            p_n.font.color.rgb = c_navy

    def add_card(slide, left, top, width, height, title=None, title_color=c_navy, fill_color=c_card_bg):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
        card.adjustments[0] = 0.02
        card.fill.solid()
        card.fill.fore_color.rgb = fill_color
        card.line.color.rgb = c_border
        card.line.width = Pt(1)

        if title:
            bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(0.45))
            bar.fill.solid()
            bar.fill.fore_color.rgb = title_color
            bar.line.color.rgb = title_color
            tb = slide.shapes.add_textbox(Inches(left + 0.18), Inches(top + 0.07), Inches(width - 0.36), Inches(0.35))
            tf = tb.text_frame
            p = tf.paragraphs[0]
            p.text = title
            p.font.name = "Calibri"
            p.font.size = Pt(14)
            p.font.bold = True
            p.font.color.rgb = c_white
        return card

    def add_bullets(slide, left, top, width, height, items, font_size=13.5, space_after=8):
        tb = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
        tf = tb.text_frame
        tf.word_wrap = True
        for i, (lead, body) in enumerate(items):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.space_after = Pt(space_after)
            if lead:
                r1 = p.add_run()
                r1.text = f"▸ {lead}: "
                r1.font.name = "Calibri"
                r1.font.size = Pt(font_size)
                r1.font.bold = True
                r1.font.color.rgb = c_navy
                r2 = p.add_run()
                r2.text = body
                r2.font.name = "Calibri"
                r2.font.size = Pt(font_size)
                r2.font.color.rgb = c_dark
            else:
                r = p.add_run()
                r.text = f"▸ {body}"
                r.font.name = "Calibri"
                r.font.size = Pt(font_size)
                r.font.color.rgb = c_dark

    def add_graph_interpretation_slide(slide_num, title, category, img_path, img_caption, takeaway_title, takeaways, highlight_stat):
        slide = prs.slides.add_slide(blank_layout)
        add_header(slide, title, category, slide_num)

        # Left Card: Graph Container
        add_card(slide, 0.5, 1.3, 7.6, 5.65, fill_color=c_white)
        if os.path.exists(img_path):
            slide.shapes.add_picture(img_path, Inches(0.62), Inches(1.42), width=Inches(7.36))
        else:
            tb_err = slide.shapes.add_textbox(Inches(1.0), Inches(3.5), Inches(6.5), Inches(1.0))
            tb_err.text_frame.paragraphs[0].text = f"[Missing figure: {os.path.basename(img_path)}]"

        cap_box = slide.shapes.add_textbox(Inches(0.65), Inches(6.55), Inches(7.3), Inches(0.35))
        p_cap = cap_box.text_frame.paragraphs[0]
        p_cap.text = img_caption
        p_cap.font.name = "Calibri"
        p_cap.font.size = Pt(10.5)
        p_cap.font.italic = True
        p_cap.font.color.rgb = c_gray

        # Right Card: "What We Understand From This Graph"
        add_card(slide, 8.3, 1.3, 4.53, 4.3, title=takeaway_title, title_color=c_navy)
        add_bullets(slide, 8.48, 1.88, 4.18, 3.6, takeaways, font_size=12.5, space_after=9)

        # Bottom-Right Highlight Callout
        add_card(slide, 8.3, 5.78, 4.53, 1.17, fill_color=RGBColor(255, 243, 224))
        hb = slide.shapes.add_textbox(Inches(8.48), Inches(5.88), Inches(4.18), Inches(0.98))
        tf_h = hb.text_frame
        tf_h.word_wrap = True
        p_h1 = tf_h.paragraphs[0]
        p_h1.text = "KEY QUANTITATIVE INSIGHT"
        p_h1.font.name = "Calibri"
        p_h1.font.size = Pt(10.5)
        p_h1.font.bold = True
        p_h1.font.color.rgb = c_accent
        p_h2 = tf_h.add_paragraph()
        p_h2.text = highlight_stat
        p_h2.font.name = "Calibri"
        p_h2.font.size = Pt(12.5)
        p_h2.font.bold = True
        p_h2.font.color.rgb = c_dark

    # =========================================================================
    # SLIDE 1: TITLE SLIDE
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_bg(s1, c_navy)
    top_bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.18))
    top_bar.fill.solid()
    top_bar.fill.fore_color.rgb = c_accent
    top_bar.line.color.rgb = c_accent

    tb1 = s1.shapes.add_textbox(Inches(0.9), Inches(1.1), Inches(11.5), Inches(4.8))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    p = tf1.paragraphs[0]
    p.text = "SYMBIOSIS STATISTICAL INSTITUTE (SSI), PUNE"
    p.font.name = "Calibri"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = RGBColor(255, 179, 102)
    p.space_after = Pt(18)

    p2 = tf1.add_paragraph()
    p2.text = "Empirical Characterization & Probabilistic Modeling of Price Formation, Volatility, and Spike Dynamics in the Indian Electricity Market (IEX)"
    p2.font.name = "Calibri"
    p2.font.size = Pt(32)
    p2.font.bold = True
    p2.font.color.rgb = c_white
    p2.space_after = Pt(22)

    p3 = tf1.add_paragraph()
    p3.text = "Proving Information Propagation from Day-Ahead Market (DAM) Bidding to Real-Time Market (RTM) Clearance via Applied Probability Distributions (Units 1–5)"
    p3.font.name = "Calibri"
    p3.font.size = Pt(17)
    p3.font.color.rgb = RGBColor(200, 220, 245)

    meta_card = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9), Inches(5.35), Inches(11.5), Inches(1.45))
    meta_card.adjustments[0] = 0.05
    meta_card.fill.solid()
    meta_card.fill.fore_color.rgb = RGBColor(18, 52, 115)
    meta_card.line.color.rgb = RGBColor(60, 105, 180)

    mtb = s1.shapes.add_textbox(Inches(1.15), Inches(5.5), Inches(11.0), Inches(1.2))
    mtf = mtb.text_frame
    mtf.word_wrap = True
    mp1 = mtf.paragraphs[0]
    mp1.text = "Course: Applied Probability Distributions (THM6242)   |   Program: M.Sc. Applied Statistics & Data Science (AY 2026–27)"
    mp1.font.name = "Calibri"
    mp1.font.size = Pt(13)
    mp1.font.bold = True
    mp1.font.color.rgb = c_white
    mp1.space_after = Pt(6)

    mp2 = mtf.add_paragraph()
    mp2.text = "Instructor: Dr. Monika Vishnoi   |   Group 05   |   GitHub Capstone: github.com/arcanekrishna/energy"
    mp2.font.name = "Calibri"
    mp2.font.size = Pt(13)
    mp2.font.color.rgb = RGBColor(190, 210, 240)

    # =========================================================================
    # SLIDE 2: WHY ELECTRICITY IS UNIQUE & MARKET ARCHITECTURE
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_header(s2, "Problem Motivation: Why Electricity Markets Need Stochastic Modeling", "1. Domain & Market Architecture", 2)

    add_card(s2, 0.6, 1.3, 5.9, 5.55, title="Physical Realities of the Indian Grid", title_color=c_navy)
    add_bullets(s2, 0.8, 1.9, 5.5, 4.7, [
        ("Zero Bulk Economic Storage", "Generation must instantaneously match consumer load every second to hold grid frequency at 50.00 Hz."),
        ("96 Daily Timeblocks", "Every 24-hour day is divided into 96 discrete 15-minute operational intervals."),
        ("The Renewable Transition", "Mid-day solar power floods the grid (10:00–15:00), followed by a massive >25,000 MW net-load ramp at sunset."),
        ("CERC Price Cap (₹10,000/MWh)", "Under CERC Petition 04/SM/2022, spot clearing prices are legally capped at ₹10,000/MWh (₹10/kWh) to curb market power.")
    ], font_size=13.5, space_after=12)

    add_card(s2, 6.8, 1.3, 5.9, 2.65, title="Day-Ahead Market (DAM): Planning (Day D-1)", title_color=c_blue)
    add_bullets(s2, 7.0, 1.88, 5.5, 1.95, [
        ("Double-Auction Window", "Cleared once daily (10:00–12:00 IST on D-1) via Social Welfare Maximization."),
        ("Physical Rationing", "When Purchase Bids > Sell Bids, unmet buyer demand cannot disappear—it spills forward into Day D.")
    ], font_size=13, space_after=8)

    add_card(s2, 6.8, 4.2, 5.9, 2.65, title="Real-Time Market (RTM): Balancing (Day D)", title_color=c_accent)
    add_bullets(s2, 7.0, 4.78, 5.5, 1.95, [
        ("48 Half-Hourly Gate Closures", "Closes just 1 hour prior to delivery to handle wind/solar forecast errors and forced plant outages."),
        ("Core Thesis", "Unsatisfied DAM bids & imbalance ratios directly drive RTM price explosions.")
    ], font_size=13, space_after=8)

    # =========================================================================
    # SLIDE 3: DATASET PROVENANCE & RAW SYNCHRONIZATION PIPELINE
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_header(s3, "Data Provenance, Raw Extraction & Synchronization Pipeline", "2. Data Engineering & Zero-Leakage Discipline", 3)

    add_card(s3, 0.6, 1.3, 5.9, 5.55, title="Official Data Sources & Raw Challenges", title_color=c_navy)
    add_bullets(s3, 0.8, 1.9, 5.5, 4.7, [
        ("Primary Source (IEX India)", "Official DAM_Market Snapshot.xlsx (3,105 raw rows) & RTM_Market Snapshot.xlsx (3,045 raw rows), Oct 3 – Nov 2, 2026."),
        ("Supporting Archives", "233,760 historical DAM blocks (2018–2024) + Grid-India (POSOCO) 5-min SCADA telemetry."),
        ("Raw Anomalies Cleaned", "Skipped 4 non-tabular metadata rows, stripped Max/Min/Avg summary footers, parsed '00:00 - 00:15' to blocks 1–96."),
        ("Temporal Alignment", "Strict inner join on (date, block_no) produced N = 2,916 synchronized operational blocks across 31 days.")
    ], font_size=13, space_after=11)

    add_card(s3, 6.8, 1.3, 5.9, 5.55, title="Engineered Features (100% Ex-Ante)", title_color=c_teal)
    add_bullets(s3, 7.0, 1.9, 5.5, 4.7, [
        ("DAM Imbalance Ratio", "Purchase Bid (MW) / Sell Bid (MW) — known at 12:00 PM on D-1. Values > 1.25 signal severe scarcity."),
        ("DAM Unsatisfied Demand", "max(0, Purchase Bid - Sell Bid) — exact MW volume forced into intra-day RTM balancing."),
        ("Harmonic Diurnal Features", "sin(2π·block/96) & cos(2π·block/96) to encode continuous 24-hour periodicity."),
        ("Strictly Lagged Targets", "P_RTM(t-4), P_RTM(t-8), P_RTM(t-16) for 1h, 2h, and 4h ex-ante evaluation (70/30 chronological split).")
    ], font_size=13, space_after=11)

    # =========================================================================
    # SLIDE 4: RESEARCH QUESTIONS & SYLLABUS ALIGNMENT
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_header(s4, "Research Formulation & Applied Probability Curriculum Mapping", "3. Research Design (Units 1–5)", 4)

    rqs = [
        ("RQ1: Multi-Horizon Forecasting Proof", "Does DAM bidding behavior predict future RTM prices & spikes (1h, 2h, 4h)?", "Ex-Ante Regression, Logistic Calibration, ROC-AUC, Brier Score", c_navy),
        ("RQ2: Conditional Expectation (Unit 1)", "How much total RTM variance is explained by DAM imbalance regimes?", "Conditional Mean E[Y|X], Var(Y|X), Law of Total Variance (Eve's Law)", c_blue),
        ("RQ3: Discrete Spike Counting (Unit 2)", "Do extreme price spikes (≥ ₹7,000) arrive randomly or cluster in bursts?", "Poisson vs. Negative Binomial MLE, Index of Dispersion (s²/x̄)", c_teal),
        ("RQ4: Continuous Fit & Hypothesis (Unit 3)", "Which density fits spot prices & does solar shift daytime vs. dusk regimes?", "Gamma/Weibull MLE, χ² GOF, Welch's t-test, Two-Sample F-test", c_accent),
        ("RQ5: Extremes & CLT Convergence (Unit 4)", "How does daily max X_(96) behave & does daily aggregation restore normality?", "Order Statistics X_(96), Lindeberg-Lévy CLT Monte Carlo Bootstrap", c_navy),
    ]
    for i, (rq_t, q_desc, math_used, col) in enumerate(rqs):
        top = 1.32 + i * 1.12
        add_card(s4, 0.6, top, 12.13, 0.98, fill_color=c_white)
        badge = s4.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(top), Inches(0.15), Inches(0.98))
        badge.fill.solid()
        badge.fill.fore_color.rgb = col
        badge.line.color.rgb = col

        tb = s4.shapes.add_textbox(Inches(0.9), Inches(top + 0.08), Inches(11.6), Inches(0.82))
        tf = tb.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        r1 = p1.add_run()
        r1.text = f"{rq_t}  —  "
        r1.font.name = "Calibri"
        r1.font.size = Pt(13.5)
        r1.font.bold = True
        r1.font.color.rgb = col
        r2 = p1.add_run()
        r2.text = q_desc
        r2.font.name = "Calibri"
        r2.font.size = Pt(13)
        r2.font.color.rgb = c_dark

        p2 = tf.add_paragraph()
        p2.text = f"Statistical Framework: {math_used}"
        p2.font.name = "Calibri"
        p2.font.size = Pt(11.5)
        p2.font.italic = True
        p2.font.color.rgb = c_gray

    # =========================================================================
    # SLIDE 5: GRAPH 1 - DIURNAL PROFILE & SOLAR DUCK CURVE
    # =========================================================================
    add_graph_interpretation_slide(
        slide_num=5,
        title="Graph 1: Intra-Day Diurnal Profile & The Solar Duck Curve",
        category="4. Exploratory Data Analysis & Physical Dynamics",
        img_path=os.path.join(nb_fig_dir, "nb_cell_04_fig_1.png"),
        img_caption="Figure 1: Mean RTM price & Interquartile Range (p25–p75) across the 96 daily 15-minute operational blocks.",
        takeaway_title="What We Understand From This Graph",
        takeaways=[
            ("Solar Belly (Blocks 40–60)", "Between 10:00 and 15:00 IST, zero-marginal-cost solar generation floods the grid, collapsing mean RTM prices to ₹1,816/MWh."),
            ("Sunset Ramp (Blocks 72–88)", "As solar drops to zero at dusk while residential load peaks, prices explode 4.42x to ₹8,021/MWh."),
            ("Severe Non-Normality", "Prices hit the ₹10,000/MWh CERC cap frequently during evening peaks, creating bimodal skew."),
            ("BESS Arbitrage Signal", "Wide +₹6,205/MWh diurnal spread proves clear economic viability for 4-hour battery storage.")
        ],
        highlight_stat="Welch's t = 46.80 (p < 1e-200) | Evening volatility is 5.80x higher than mid-day solar (F = 5.80)."
    )

    # =========================================================================
    # SLIDE 6: GRAPH 2 - EMPIRICAL FORECASTING PROOF (RQ1)
    # =========================================================================
    add_graph_interpretation_slide(
        slide_num=6,
        title="Graph 2: Empirical Proof — DAM Bidding Predicts RTM Prices (RQ1)",
        category="5. Multi-Horizon Forecasting Proof (Zero Data Leakage)",
        img_path=os.path.join(nb_fig_dir, "nb_cell_09_fig_2.png"),
        img_caption="Figure 2: 4-Hour Ahead out-of-sample RTM forecast: Actual Price (black) vs. Baseline (red) vs. DAM-Informed (blue).",
        takeaway_title="What We Understand From This Graph",
        takeaways=[
            ("Autoregressive Decay", "At a 4-hour horizon (lag=16), lagged RTM memory fades; the red Baseline curve lags behind and misses sudden spikes (R² = 0.4737)."),
            ("DAM Anchors the Forecast", "The blue DAM-Informed model tracks actual evening spikes accurately because Day-Ahead unmet demand already warned of the scarcity."),
            ("22.25% Error Reduction", "MAE drops from ₹1,233.6/MWh to ₹959.1/MWh, while R² jumps +18.75 percentage points to 0.6612."),
            ("Spike Early Warning", "Logistic spike classifier reaches ROC-AUC = 0.9663 and cuts Brier calibration error nearly in half (0.0799 → 0.0401).")
        ],
        highlight_stat="4-Hour Ahead: R² jumps 0.4737 → 0.6612 (+18.75 pts) | Spike ROC-AUC = 0.9663 | Brier Score -49.8%."
    )

    # =========================================================================
    # SLIDE 7: FORECASTING METRICS TABLE (1H, 2H, 4H)
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    add_header(s7, "Multi-Horizon Forecasting Benchmark Summary (1h, 2h, 4h Ahead)", "5. Quantitative Proof Across Horizons", 7)

    # Table 1 Card
    add_card(s7, 0.6, 1.3, 12.13, 2.65, title="Table 1: Continuous Price Level Regression (Gradient Boosting / Ridge)", title_color=c_navy)
    rows1 = [
        ["Forecast Horizon", "Baseline MAE", "DAM-Informed MAE", "MAE Improvement", "Baseline R²", "DAM-Informed R²", "R² Gain (+)"],
        ["1 Hour Ahead (lag=4)", "₹865.1", "₹854.4", "+1.24%", "0.7101", "0.7221", "+0.0120"],
        ["2 Hours Ahead (lag=8)", "₹1,099.6", "₹950.4", "+13.57%", "0.5964", "0.6659", "+0.0695"],
        ["4 Hours Ahead (lag=16)", "₹1,233.6", "₹959.1", "+22.25%", "0.4737", "0.6612", "+0.1875"],
    ]
    t1 = s7.shapes.add_table(4, 7, Inches(0.8), Inches(1.88), Inches(11.73), Inches(1.88)).table
    for r_idx, row in enumerate(rows1):
        for c_idx, val in enumerate(row):
            cell = t1.cell(r_idx, c_idx)
            cell.text = val
            p = cell.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER
            p.font.name = "Calibri"
            p.font.size = Pt(12.5)
            if r_idx == 0:
                cell.fill.solid()
                cell.fill.fore_color.rgb = RGBColor(225, 235, 248)
                p.font.bold = True
                p.font.color.rgb = c_navy
            elif r_idx == 3 and c_idx in (3, 6):
                p.font.bold = True
                p.font.color.rgb = c_accent

    # Table 2 Card
    add_card(s7, 0.6, 4.2, 12.13, 2.65, title="Table 2: Extreme Price Spike Classification (Target: P_RTM ≥ ₹7,000/MWh)", title_color=c_teal)
    rows2 = [
        ["Forecast Horizon", "Baseline ROC-AUC", "DAM-Informed ROC-AUC", "Baseline Brier Score", "DAM-Informed Brier Score", "Brier Reduction"],
        ["1 Hour Ahead (lag=4)", "0.9727", "0.9811", "0.0504", "0.0373", "-26.0%"],
        ["2 Hours Ahead (lag=8)", "0.9582", "0.9633", "0.0633", "0.0405", "-36.0%"],
        ["4 Hours Ahead (lag=16)", "0.9342", "0.9663", "0.0799", "0.0401", "-49.8%"],
    ]
    t2 = s7.shapes.add_table(4, 6, Inches(0.8), Inches(4.78), Inches(11.73), Inches(1.88)).table
    for r_idx, row in enumerate(rows2):
        for c_idx, val in enumerate(row):
            cell = t2.cell(r_idx, c_idx)
            cell.text = val
            p = cell.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER
            p.font.name = "Calibri"
            p.font.size = Pt(12.5)
            if r_idx == 0:
                cell.fill.solid()
                cell.fill.fore_color.rgb = RGBColor(220, 240, 238)
                p.font.bold = True
                p.font.color.rgb = c_teal
            elif r_idx == 3 and c_idx in (2, 5):
                p.font.bold = True
                p.font.color.rgb = c_accent

    # =========================================================================
    # SLIDE 8: GRAPH 3 - CONDITIONAL EXPECTATION & EVE'S LAW (RQ2)
    # =========================================================================
    add_graph_interpretation_slide(
        slide_num=8,
        title="Graph 3: Conditional Expectation & Law of Total Variance (RQ2)",
        category="6. Unit 1 — Joint & Conditional Distributions",
        img_path=os.path.join(fig_dir, "fig2_conditional_expectation_regimes.png"),
        img_caption="Figure 3: Conditional RTM price distributions stratified by Day-Ahead Imbalance Regime (Deficit, Balanced, Surplus).",
        takeaway_title="What We Understand From This Graph",
        takeaways=[
            ("Sharp Regime Bifurcation", "When DAM Imbalance Ratio > 1.25 (Deficit, 64.6% of blocks), mean RTM price surges to ₹7,408.81/MWh."),
            ("Balanced & Surplus Regimes", "Balanced days average ₹2,993/MWh, while Surplus days (Ratio < 0.80) drop to ₹1,838/MWh—a 4x price gap."),
            ("Tower Property Exact Match", "Iterated expectation E[E[Y|X]] = ₹5,596.76 matches the unconditional mean E[Y] to 8 decimal places."),
            ("Eve's Law Decomposition", "Var(Y) = E[Var(Y|X)] + Var(E[Y|X]) proves 49.10% of total market variance is driven strictly by DAM regime!")
        ],
        highlight_stat="Explained Variance Ratio η² = Var(E[Y|X]) / Var(Y) = 49.10% (Verified to < 1e-8 precision)."
    )

    # =========================================================================
    # SLIDE 9: GRAPH 4 - DISCRETE SPIKE COUNTING (RQ3)
    # =========================================================================
    add_graph_interpretation_slide(
        slide_num=9,
        title="Graph 4: Discrete Spike Counts — Poisson vs. Negative Binomial (RQ3)",
        category="7. Unit 2 — Discrete Probability Distributions",
        img_path=os.path.join(nb_fig_dir, "nb_cell_13_fig_3.png"),
        img_caption="Figure 4: Empirical daily spike count histogram vs. fitted Poisson(λ=35.03) and Negative Binomial(r=1.80, p=0.0488).",
        takeaway_title="What We Understand From This Graph",
        takeaways=[
            ("Poisson Failure (Blue Curve)", "Poisson assumes independent, memoryless arrivals (Mean = Variance = 35.03). Its narrow bell completely misses real extremes."),
            ("Severe Overdispersion", "Observed daily spike variance is 718.57 — a Dispersion Ratio (s²/x̄) of 20.51x greater than the mean!"),
            ("Why Spikes Cluster", "Heatwaves, coal shortages, and unit trips persist for hours/days, creating bursty contagion across blocks."),
            ("Negative Binomial Success", "Modeling heterogeneity via Gamma-Poisson mixture (r̂=1.795) matches empirical variance (718.57) exactly.")
        ],
        highlight_stat="Index of Dispersion s² / k̄ = 20.512 >> 1.0 → Rejects memoryless Poisson; confirms spike clustering."
    )

    # =========================================================================
    # SLIDE 10: GRAPH 5 - CONTINUOUS DENSITIES & CERC PRICE CAP (RQ4)
    # =========================================================================
    add_graph_interpretation_slide(
        slide_num=10,
        title="Graph 5: Continuous Price Densities & CERC Ceiling Truncation (RQ4)",
        category="8. Unit 3 — Continuous Distributions & MLE",
        img_path=os.path.join(fig_dir, "fig4_continuous_price_gamma_weibull.png"),
        img_caption="Figure 5: Empirical positive spot prices fitted with Gamma (α=1.91, θ=2953) & Weibull (c=1.58, λ=6273) via MLE.",
        takeaway_title="What We Understand From This Graph",
        takeaways=[
            ("Newton-Raphson Verification", "From-scratch digamma MLE solver matches SciPy Gamma parameters to 14 decimal places (|Δα| = 9.77e-15)."),
            ("The ₹10,000 Boundary Pile-Up", "Notice the huge empirical spike at the right edge [9,000–10,000] containing 1,051 blocks."),
            ("Regulatory Truncation Effect", "In an uncapped market, extreme shortages would clear at ₹20k–₹50k/MWh. The ₹10,000 cap forces all tail mass onto the boundary."),
            ("Chi-Square Diagnosis", "88.15% of total χ² divergence (6,120.5 / 6,943.2) comes solely from this single capped top bin.")
        ],
        highlight_stat="88.15% of Chi-Square GOF divergence originates at the statutory ₹10,000/MWh CERC price ceiling."
    )

    # =========================================================================
    # SLIDE 11: GRAPH 6 - EXTREME ORDER STATISTICS X_(96) (RQ5a)
    # =========================================================================
    add_graph_interpretation_slide(
        slide_num=11,
        title="Graph 6: Extreme Value Order Statistics — Daily Peak Price X_(96)",
        category="9. Unit 4 — Order Statistics of 96-Block Schedules",
        img_path=os.path.join(fig_dir, "fig5_order_statistics_daily_max.png"),
        img_caption="Figure 6: Distribution of Daily Maximum Price X_(96) = max(X_1, ..., X_96) across 31 trading days.",
        takeaway_title="What We Understand From This Graph",
        takeaways=[
            ("Order Statistic Formulation", "For each 96-block trading day, daily peak risk is governed by X_(96) with theoretical CDF F_(96)(x) = [F(x)]^96."),
            ("Ceiling Saturation", "28 out of 31 trading days (90.32%) hit the ₹10,000/MWh regulatory ceiling at least once during the day."),
            ("Compressed Peak Distribution", "Mean daily maximum is ₹9,726.79/MWh with a tight standard deviation of ₹888.72/MWh."),
            ("Operational Reality", "Hitting ₹10,000/MWh daily is not an outlier event—it is a routine structural feature of peak Indian grid demand.")
        ],
        highlight_stat="90.32% of days (28 of 31) hit the ₹10,000/MWh ceiling | Mean Daily Max X_(96) = ₹9,726.79/MWh."
    )

    # =========================================================================
    # SLIDE 12: GRAPH 7 - CENTRAL LIMIT THEOREM CONVERGENCE (RQ5b)
    # =========================================================================
    add_graph_interpretation_slide(
        slide_num=12,
        title="Graph 7: Central Limit Theorem Convergence on Procurement Sums",
        category="10. Unit 4 & 5 — Lindeberg-Lévy CLT Bootstrap",
        img_path=os.path.join(nb_fig_dir, "nb_cell_18_fig_4.png"),
        img_caption="Figure 7: Standardized sampling distributions (3,000 bootstraps) for block sizes n = 1, 4, 16, and 96 vs. N(0, 1).",
        takeaway_title="What We Understand From This Graph",
        takeaways=[
            ("n = 1 (15-min Spot)", "Severely non-normal and bimodal (Excess Kurtosis = -1.57) due to solar lows and ₹10,000 ceiling hits."),
            ("n = 4 & 16 (1h to 4h Blocks)", "As procurement duration aggregates across blocks, skewness and kurtosis decay rapidly toward zero."),
            ("n = 96 (Full 24h Portfolio)", "Daily average procurement cost aligns cleanly with the red N(0, 1) Gaussian curve (Skew = 0.022, Kurt = 0.017)."),
            ("Risk Budgeting Validation", "Proves State DISCOMs can safely apply classical Gaussian Value-at-Risk (VaR) for daily budgets, despite wild 15-min spikes.")
        ],
        highlight_stat="At n = 96 (1-day portfolio): Skewness = +0.0222, Excess Kurtosis = +0.0174 → Gaussian Normality Restored!"
    )

    # =========================================================================
    # SLIDE 13: RIGOROUS MATHEMATICAL & STATISTICAL TOOLKIT
    # =========================================================================
    s13 = prs.slides.add_slide(blank_layout)
    add_header(s13, "Rigorous Mathematical Derivations & Scratch Implementations", "11. Theoretical & Computational Verification", 13)

    add_card(s13, 0.6, 1.3, 5.9, 5.55, title="From-Scratch Numerical Verification", title_color=c_navy)
    add_bullets(s13, 0.8, 1.9, 5.5, 4.7, [
        ("Eve's Law / Total Variance", "Verified Var(Y) = E[Var(Y|X)] + Var(E[Y|X]) = 6,339,197 + 6,115,223 = 12,454,420 (Error < 10⁻⁸)."),
        ("Gamma MLE via Newton-Raphson", "Solved ln(α) - ψ(α) = ln(x̄) - mean(ln x) using digamma & trigamma updates; exact match to SciPy (9.77e-15)."),
        ("Negative Binomial Dispersion", "Derived Gamma-Poisson mixture Var(K) = μ + μ²/r, capturing 20.5x variance-to-mean overdispersion."),
        ("Welch's Satterthwaite Test", "Computed unequal-variance t-statistic (t = 46.80, ν = 650.6 df) from scratch without pooled-variance bias.")
    ], font_size=13, space_after=11)

    add_card(s13, 6.8, 1.3, 5.9, 5.55, title="Validation & Anti-Leakage Safeguards", title_color=c_teal)
    add_bullets(s13, 7.0, 1.9, 5.5, 4.7, [
        ("Chronological 70/30 Split", "Strictly prevents future data from leaking into historical training windows (no random K-fold cheating)."),
        ("Ex-Ante Feature Lock", "Forecasts at horizon h only access DAM bids (settled D-1) and RTM lags strictly ≤ t - h."),
        ("Calibration Metrics", "Evaluated probabilistic spike predictions via proper scoring rules (Brier Score) alongside ranking (ROC-AUC)."),
        ("Dual-Mode Reproducibility", "Google Colab notebook parses raw IEX Excel snapshots directly or pulls verified CSV from GitHub.")
    ], font_size=13, space_after=11)

    # =========================================================================
    # SLIDE 14: STAKEHOLDER RECOMMENDATIONS & REAL-WORLD IMPACT
    # =========================================================================
    s14 = prs.slides.add_slide(blank_layout)
    add_header(s14, "Actionable Insights for Grid Operators, Utilities & Regulators", "12. Industrial & Policy Impact", 14)

    cards_14 = [
        ("For State DISCOMs (Buyers)", c_navy, [
            ("Pre-Hedge Deficit Regimes", "When DAM Imbalance Ratio > 1.25, avoid deferring load to RTM—expected spot price jumps to ₹7,409/MWh with 90% cap-hit risk."),
            ("Daily Portfolio VaR", "Use Gaussian Value-at-Risk (μ + 1.645σ) on daily procurement budgets (justified by n=96 CLT convergence), never on 15-min spot intervals.")
        ]),
        ("For Battery Storage (BESS)", c_teal, [
            ("Proven Arbitrage Spread", "Charge during mid-day solar valley (₹1,816/MWh) and discharge during evening ramp (₹8,021/MWh) for a +₹6,205/MWh spread."),
            ("Spike Clustering Value", "Negative Binomial clustering (r=1.80) creates multi-hour sustained peak blocks ideal for 2-to-4 hour Li-ion storage dispatch.")
        ]),
        ("For CERC Regulators", c_accent, [
            ("Cap Distortion Signal", "88.15% of distribution misfit sits on the ₹10,000 ceiling bin—showing acute scarcity signals are being truncated."),
            ("Policy Evolution", "Supplement flat energy price caps with ancillary reserve markets and dynamic capacity payments for fast-ramping peaking units.")
        ])
    ]
    for i, (ct, col, items) in enumerate(cards_14):
        left = 0.6 + i * 4.1
        add_card(s14, left, 1.35, 3.85, 5.45, title=ct, title_color=col)
        add_bullets(s14, left + 0.18, 1.98, 3.5, 4.6, items, font_size=12.5, space_after=14)

    # =========================================================================
    # SLIDE 15: CONCLUSION & DELIVERABLES SUMMARY
    # =========================================================================
    s15 = prs.slides.add_slide(blank_layout)
    set_bg(s15, c_navy)
    top_b15 = s15.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.15))
    top_b15.fill.solid()
    top_b15.fill.fore_color.rgb = c_accent
    top_b15.line.color.rgb = c_accent

    tb15 = s15.shapes.add_textbox(Inches(0.9), Inches(0.8), Inches(11.5), Inches(1.2))
    tf15 = tb15.text_frame
    p15 = tf15.paragraphs[0]
    p15.text = "Conclusion: Probability Theory Unlocks Grid Intelligence"
    p15.font.name = "Calibri"
    p15.font.size = Pt(30)
    p15.font.bold = True
    p15.font.color.rgb = c_white

    p15_sub = tf15.add_paragraph()
    p15_sub.text = "Summary of Proven Empirical Findings & Complete Academic Submission Suite"
    p15_sub.font.name = "Calibri"
    p15_sub.font.size = Pt(15)
    p15_sub.font.color.rgb = RGBColor(190, 210, 240)

    summary_items = [
        ("1. DAM Predicts RTM", "DAM bidding features cut 4-hour RTM MAE by 22.25%, boost R² by +18.75 pts (0.6612), and achieve 0.9663 spike ROC-AUC."),
        ("2. Variance Explained", "Eve's Law proves DAM market imbalance regimes explain 49.10% of total intra-day RTM price variance."),
        ("3. Clustered Extremes", "Daily spikes show 20.51x overdispersion (Negative Binomial, not Poisson) and hit the ₹10,000 CERC cap on 90.3% of days."),
        ("4. Normality Restored", "Lindeberg-Lévy CLT guarantees Gaussian convergence at n=96 blocks (Skewness = 0.02), validating utility VaR budgeting.")
    ]
    for i, (lead, body) in enumerate(summary_items):
        top = 2.15 + i * 0.95
        card = s15.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9), Inches(top), Inches(11.5), Inches(0.8))
        card.adjustments[0] = 0.08
        card.fill.solid()
        card.fill.fore_color.rgb = RGBColor(18, 52, 115)
        card.line.color.rgb = RGBColor(60, 105, 180)
        ctb = s15.shapes.add_textbox(Inches(1.1), Inches(top + 0.14), Inches(11.1), Inches(0.55))
        ctf = ctb.text_frame
        ctf.word_wrap = True
        cp = ctf.paragraphs[0]
        r1 = cp.add_run()
        r1.text = f"{lead}:  "
        r1.font.name = "Calibri"
        r1.font.size = Pt(14)
        r1.font.bold = True
        r1.font.color.rgb = RGBColor(255, 179, 102)
        r2 = cp.add_run()
        r2.text = body
        r2.font.name = "Calibri"
        r2.font.size = Pt(13.5)
        r2.font.color.rgb = c_white

    foot15 = s15.shapes.add_textbox(Inches(0.9), Inches(6.3), Inches(11.5), Inches(0.8))
    ftf15 = foot15.text_frame
    fp15 = ftf15.paragraphs[0]
    fp15.alignment = PP_ALIGN.CENTER
    fp15.text = "Thank You! Questions & Viva Discussion"
    fp15.font.name = "Calibri"
    fp15.font.size = Pt(22)
    fp15.font.bold = True
    fp15.font.color.rgb = c_white

    fp15_2 = ftf15.add_paragraph()
    fp15_2.alignment = PP_ALIGN.CENTER
    fp15_2.text = "Repository: https://github.com/arcanekrishna/energy  |  Notebook: SSI_THM6242_Applied_Probability_Project.ipynb"
    fp15_2.font.name = "Calibri"
    fp15_2.font.size = Pt(12)
    fp15_2.font.color.rgb = RGBColor(180, 205, 240)

    os.makedirs(os.path.dirname(out_pptx), exist_ok=True)
    prs.save(out_pptx)
    print(f"Presentation successfully created at: {out_pptx} (15 slides)")

if __name__ == "__main__":
    create_presentation()
