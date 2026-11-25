import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml

doc = docx.Document()

# Page setup: Standard A4 with compact 0.75 in margins so everything sits on exactly 1 page
for section in doc.sections:
    section.page_width = Inches(8.27)
    section.page_height = Inches(11.69)
    section.top_margin = Inches(0.7)
    section.bottom_margin = Inches(0.7)
    section.left_margin = Inches(0.8)
    section.right_margin = Inches(0.8)

NAVY = RGBColor(27, 54, 93)     # #1B365D - Deep Academic Navy
GREY = RGBColor(100, 110, 120)
BODY_COLOR = RGBColor(40, 45, 50)

def add_section_header(title):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(title)
    run.font.name = 'Calibri'
    run.font.size = Pt(11)
    run.font.bold = True
    run.font.color.rgb = NAVY
    # Add a thin bottom line for executive visual separation
    pBdr = parse_xml(
        '<w:pBdr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        '<w:bottom w:val="single" w:sz="6" w:space="2" w:color="1B365D"/>'
        '</w:pBdr>'
    )
    p._p.get_or_add_pPr().append(pBdr)
    return p

# Eyebrow / Label
p_eye = doc.add_paragraph()
p_eye.paragraph_format.space_before = Pt(0)
p_eye.paragraph_format.space_after = Pt(2)
r_eye = p_eye.add_run('ACADEMIC RESEARCH PROJECT SYNOPSIS')
r_eye.font.name = 'Calibri'
r_eye.font.size = Pt(9)
r_eye.font.bold = True
r_eye.font.color.rgb = GREY

# Document Title / Topic
p_title = doc.add_paragraph()
p_title.paragraph_format.space_before = Pt(0)
p_title.paragraph_format.space_after = Pt(8)
p_title.paragraph_format.keep_with_next = True
r_title = p_title.add_run(
    'Early Warning System for Non-Performing Assets in Indian Commercial Banks: '
    'An Explainable Machine Learning and Dynamic Econometric Approach'
)
r_title.font.name = 'Calibri'
r_title.font.size = Pt(14)
r_title.font.bold = True
r_title.font.color.rgb = NAVY

# 1. OBJECTIVES
add_section_header('PROJECT OBJECTIVES')

p_pobj = doc.add_paragraph()
p_pobj.paragraph_format.space_before = Pt(2)
p_pobj.paragraph_format.space_after = Pt(3)
p_pobj.paragraph_format.line_spacing = 1.12
r_po_label = p_pobj.add_run('Primary Objective: ')
r_po_label.font.name = 'Calibri'
r_po_label.font.size = Pt(10)
r_po_label.font.bold = True
r_po_label.font.color.rgb = NAVY

r_po_text = p_pobj.add_run(
    'To design, implement, and validate a supervisory Early Warning System (EWS) that integrates '
    'dynamic panel econometrics with explainable machine learning to predict bank asset quality distress '
    'and regulatory Prompt Corrective Action intervention thresholds 12 to 24 months in advance.'
)
r_po_text.font.name = 'Calibri'
r_po_text.font.size = Pt(10)
r_po_text.font.color.rgb = BODY_COLOR

objectives = [
    ('Historical Data Reconciliation: ', 'Reconstruct RBI banking archives across historical merger ruptures into a continuous 21-year macro panel and an 87-bank longitudinal micro-panel (649 model-ready bank-years, 2013–2024).'),
    ('Dynamic Econometric Modeling: ', 'Quantify asset quality persistence (alpha = 0.5457) and resolve the credit boom inversion paradox, confirming that rapid credit expansion seeds defaults with a 2-year lag (beta = +0.0393, p = 0.013).'),
    ('Supervisory Distress Classification: ', 'Train gradient-boosted trees (XGBoost) to predict statutory RBI Prompt Corrective Action (PCA) Threshold 1 breaches (GNPA >= 6.0%), achieving 76.3% out-of-time accuracy and 0.710 ROC-AUC.'),
    ('Explainable AI (TreeSHAP): ', 'Provide transparent, audit-ready risk explanations for central bank supervisors, identifying non-linear tipping points such as the Return on Assets "profitability cliff" (RoA < 0.50%).'),
    ('Macroprudential Stress Testing: ', 'Simulate multi-dimensional economic shocks via logit-bounded satellite projections to project post-shock Capital-to-Risk-Weighted Assets Ratios (CRAR) and identify banks breaching the 9.0% regulatory capital floor.')
]

for title, desc in objectives:
    bp = doc.add_paragraph(style='List Bullet')
    bp.paragraph_format.space_before = Pt(1)
    bp.paragraph_format.space_after = Pt(1)
    bp.paragraph_format.line_spacing = 1.1
    rt = bp.add_run(title)
    rt.font.name = 'Calibri'
    rt.font.size = Pt(9.5)
    rt.font.bold = True
    rt.font.color.rgb = NAVY
    rd = bp.add_run(desc)
    rd.font.name = 'Calibri'
    rd.font.size = Pt(9.5)
    rd.font.color.rgb = BODY_COLOR

# 2. ABSTRACT
add_section_header('ABSTRACT')

p_abs = doc.add_paragraph()
p_abs.paragraph_format.space_before = Pt(2)
p_abs.paragraph_format.space_after = Pt(4)
p_abs.paragraph_format.line_spacing = 1.12
p_abs.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

r_abs = p_abs.add_run(
    'Early detection of banking asset quality distress is essential for financial stability and macroprudential regulation. '
    'However, supervisory surveillance faces an operational dilemma: classical linear econometric models provide structural macroeconomic interpretability '
    'but miss non-linear default tipping points, whereas complex machine learning models often operate as uninterpretable black boxes and fail to beat simple '
    'persistence in forecasting continuous gradual drifts. This paper presents an integrated dual-engine Supervisory Technology (SupTech) early warning '
    'framework evaluated on the Indian Scheduled Commercial Banking sector. First, resolving historical statistical ruptures caused by public sector bank '
    'mergers, we reconstruct an uninterrupted 21-year macro panel and synthesize an extensive micro-longitudinal panel of 649 bank-year observations spanning '
    '87 commercial banks over 2013–2024. Second, dynamic panel econometric estimation resolves Nickell endogeneity bias, establishing significant asset quality '
    'persistence (alpha = 0.5457, t = 9.13, p < 0.001) and confirming that credit expansion increases default formation with a two-year lag (beta = +0.0393, p = 0.013). '
    'Third, under strict out-of-time walk-forward validation (Train <= 2021, Test >= 2022), we demonstrate that while persistence dominates continuous point forecasting, '
    'an Extreme Gradient Boosting (XGBoost) classifier decisively outperforms classical logistic regression in predicting statutory Reserve Bank of India Prompt '
    'Corrective Action (PCA) Threshold 1 breaches (GNPA >= 6.0%), achieving an ROC-AUC of 0.710 versus 0.650 and an accuracy of 76.3% versus 63.5%. '
    'Using TreeSHAP game-theoretic explainability, we identify non-linear supervisory thresholds, revealing an exponential default risk surge when bank Return on '
    'Assets drops below 0.50% under elevated credit-deposit leverage. Finally, we formulate a logit-bounded satellite stress-testing module integrated with a '
    'micro-prudential capital adequacy simulation, projecting post-shock Capital to Risk-Weighted Assets Ratios (CRAR) under adverse macro scenarios. '
    'This architecture provides central banks and commercial lenders with an empirical, transparent, and policy-actionable early warning platform.'
)
r_abs.font.name = 'Calibri'
r_abs.font.size = Pt(9.5)
r_abs.font.color.rgb = BODY_COLOR

# 3. KEYWORDS
p_kw = doc.add_paragraph()
p_kw.paragraph_format.space_before = Pt(3)
p_kw.paragraph_format.space_after = Pt(0)
r_kw_label = p_kw.add_run('Keywords: ')
r_kw_label.font.name = 'Calibri'
r_kw_label.font.size = Pt(9.5)
r_kw_label.font.bold = True
r_kw_label.font.color.rgb = NAVY

r_kw_text = p_kw.add_run(
    'Non-Performing Assets (NPAs), Indian Banking System, Early Warning System (EWS), Explainable AI, '
    'XGBoost, TreeSHAP, Dynamic Panel Econometrics, Prompt Corrective Action (PCA), Macroprudential Stress Testing, Capital Adequacy (CRAR).'
)
r_kw_text.font.name = 'Calibri'
r_kw_text.font.size = Pt(9.5)
r_kw_text.font.italic = True
r_kw_text.font.color.rgb = BODY_COLOR

# Save to both papers directory and root directory for convenience
doc.save('papers/Project_Topic_Objectives_and_Abstract.docx')
doc.save('Project_Topic_Objectives_and_Abstract.docx')
print('Successfully generated Word documents!')
