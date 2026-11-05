import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def create_declaration():
    doc = Document()
    for s in doc.sections:
        s.page_width = Inches(8.27)
        s.page_height = Inches(11.69)
        s.top_margin = Inches(1.0)
        s.bottom_margin = Inches(1.0)
        s.left_margin = Inches(1.0)
        s.right_margin = Inches(1.0)

    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r1 = p_inst.add_run("SYMBIOSIS STATISTICAL INSTITUTE [SSI]\nSYMBIOSIS INTERNATIONAL (DEEMED UNIVERSITY), PUNE\n")
    r1.bold = True
    r1.font.size = Pt(13)
    r1.font.color.rgb = RGBColor(15, 50, 110)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r2 = p_sub.add_run("M.Sc. Applied Statistics & Data Science (SEM-I Batch-2026-2028)\nCourse: Applied Probability Distributions (THM6242)\nSubject Teacher: Dr. Monika Vishnoi\n")
    r2.font.size = Pt(11)
    r2.italic = True

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(12)
    p_title.paragraph_format.space_after = Pt(18)
    r_t = p_title.add_run("STUDENT DECLARATION AND CONTRIBUTION SHEET\n(Internal Component III & IV)")
    r_t.bold = True
    r_t.font.size = Pt(14)
    r_t.font.color.rgb = RGBColor(10, 40, 95)

    p_body = doc.add_paragraph()
    p_body.paragraph_format.line_spacing = 1.5
    p_body.paragraph_format.space_after = Pt(12)
    p_body.add_run(
        "We hereby declare that the project titled 'Empirical Characterization and Probabilistic Modeling of Price Formation, "
        "Extreme Volatility, and Daily Spike Dynamics in the Indian Electricity Market (IEX)' submitted towards the partial fulfillment "
        "of Internal Component-III (Project) and Component-IV (Presentation & Viva) in Applied Probability Distributions (THM6242) "
        "is an authentic record of our original statistical work carried out under the guidance of Dr. Monika Vishnoi.\n\n"
        "We further confirm that:\n"
        "1. All theoretical mathematical formulations and proofs (Units 1 to 4) were written in our own words.\n"
        "2. All core computational steps—including method of moments estimation, numerical maximum likelihood optimization via digamma inversion, "
        "chi-square goodness-of-fit testing with bin pooling, and Monte Carlo Central Limit Theorem convergence routines—were implemented "
        "from first principles using native NumPy arrays, and standard libraries (scipy.stats) were used solely for cross-validation.\n"
        "3. A hand-solved 5-observation numerical example with complete step-by-step arithmetic was solved and verified.\n"
        "4. All open-source datasets from the Indian Energy Exchange (IEX) and Grid-India (NLDC) have been duly cited."
    )

    doc.add_heading("Task Contribution Matrix", level=2)
    tbl = doc.add_table(rows=1, cols=4)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["Member Name", "PRN / Roll No.", "Specific Contribution / Theory Unit", "Signature"]
    widths = [Inches(1.5), Inches(1.3), Inches(2.2), Inches(1.27)]
    for i, h in enumerate(headers):
        tbl.rows[0].cells[i].text = h
        tbl.rows[0].cells[i].width = widths[i]
        shd = parse_xml(r'<w:shd {} w:fill="1F497D"/>'.format(nsdecls('w')))
        tbl.rows[0].cells[i]._tc.get_or_add_tcPr().append(shd)
        p = tbl.rows[0].cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p.runs:
            r.bold = True
            r.font.size = Pt(10)
            r.font.color.rgb = RGBColor(255, 255, 255)

    data = [
        ["Student 1 (Lead)", "PRN-001", "Unit 1: Conditional Expectation & Total Variance derivation, NumPy engine.", ""],
        ["Student 2", "PRN-002", "Unit 2: Discrete (Poisson/NB) & Continuous (Gamma/Weibull) MLE routines.", ""],
        ["Student 3", "PRN-003", "Unit 3: Chi-Square Goodness-of-Fit from scratch, Welch's t & F-tests.", ""],
        ["Student 4", "PRN-004", "Unit 4: Order Statistics X_(96) CDF, Monte Carlo CLT simulation & Report.", ""]
    ]
    for row_idx, r_data in enumerate(data):
        row_cells = tbl.add_row().cells
        bg = "F7F9FB" if row_idx % 2 == 1 else "FFFFFF"
        for c_idx, val in enumerate(r_data):
            row_cells[c_idx].text = val
            row_cells[c_idx].width = widths[c_idx]
            shd = parse_xml(r'<w:shd {} w:fill="{}"/>'.format(nsdecls('w'), bg))
            row_cells[c_idx]._tc.get_or_add_tcPr().append(shd)
            p = row_cells[c_idx].paragraphs[0]
            for r in p.runs:
                r.font.size = Pt(9.5)

    p_sig = doc.add_paragraph()
    p_sig.paragraph_format.space_before = Pt(36)
    p_sig.add_run(
        "Date of Submission: November 05, 2026\n"
        "Place: Pune, Maharashtra\n\n\n\n"
        "_____________________________\n"
        "Verified & Approved by:\n"
        "Dr. Monika Vishnoi\n"
        "Course Teacher & Assistant Professor\n"
        "Symbiosis Statistical Institute, Pune"
    )
    p_sig.runs[0].font.size = Pt(11)

    out = '/Users/krishnagupta/Downloads/inte/indian_power_market/academic_submission/declaration/Student_Declaration_and_Contribution_Sheet.docx'
    doc.save(out)
    print("Declaration document saved at:", out)

if __name__ == '__main__':
    create_declaration()
