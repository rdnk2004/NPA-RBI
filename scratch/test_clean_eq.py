import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.enum.table import WD_TABLE_ALIGNMENT

def test_clean_equation():
    doc = Document()
    sec = doc.sections[0]
    sec.top_margin = Inches(0.75)
    sec.bottom_margin = Inches(1.0)
    sec.left_margin = Inches(0.625)
    sec.right_margin = Inches(0.625)

    # In IEEE standard conference format, column width is 3.5 inches
    # An equation paragraph has center tab at 1.75" and right tab at 3.5"
    p = doc.add_paragraph()
    p.paragraph_format.tab_stops.add_tab_stop(Inches(1.75), WD_TAB_ALIGNMENT.CENTER)
    p.paragraph_format.tab_stops.add_tab_stop(Inches(3.5), WD_TAB_ALIGNMENT.RIGHT)
    p.paragraph_format.space_before = Pt(3)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.first_line_indent = Inches(0)

    # Add tab to center
    p.add_run("\t")

    # Equation 1: GNPA_i,t = α_0 + X_i,t^⊤ β + μ_i + ε_i,t
    r = p.add_run("GNPA")
    r.font.italic = True
    r = p.add_run("i,t")
    r.font.subscript = True
    r = p.add_run(" = ")
    r = p.add_run("α")
    r.font.italic = True
    r = p.add_run("0")
    r.font.subscript = True
    r = p.add_run(" + ")
    r = p.add_run("X")
    r.font.bold = True
    r = p.add_run("i,t")
    r.font.subscript = True
    r = p.add_run("⊤")
    r.font.superscript = True
    r = p.add_run(" ")
    r = p.add_run("β")
    r.font.bold = True
    r = p.add_run(" + ")
    r = p.add_run("μ")
    r.font.italic = True
    r = p.add_run("i")
    r.font.subscript = True
    r = p.add_run(" + ")
    r = p.add_run("ε")
    r.font.italic = True
    r = p.add_run("i,t")
    r.font.subscript = True

    # Tab to right and equation number
    p.add_run("\t")
    r_num = p.add_run("(1)")
    r_num.font.name = "Times New Roman"
    r_num.font.size = Pt(10)

    doc.save("scratch/test_tab_eq.docx")
    print("test_tab_eq.docx saved successfully!")

test_clean_equation()
