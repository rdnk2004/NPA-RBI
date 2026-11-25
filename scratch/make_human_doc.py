import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

doc = docx.Document()

# Standard A4 page setup with natural 0.8 in margins (fits cleanly on 1 page)
for section in doc.sections:
    section.page_width = Inches(8.27)
    section.page_height = Inches(11.69)
    section.top_margin = Inches(0.75)
    section.bottom_margin = Inches(0.75)
    section.left_margin = Inches(0.8)
    section.right_margin = Inches(0.8)

# Natural human document colors (standard professional black/charcoal)
BLACK = RGBColor(0, 0, 0)
DARK = RGBColor(30, 30, 30)

# Document Title (Centered, Clean, Academic)
p_title = doc.add_paragraph()
p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_title.paragraph_format.space_before = Pt(0)
p_title.paragraph_format.space_after = Pt(12)
p_title.paragraph_format.line_spacing = 1.15

r_title = p_title.add_run(
    'Early Warning System for Non-Performing Assets in Indian Commercial Banks:\n'
    'An Explainable Machine Learning and Dynamic Econometric Approach'
)
r_title.font.name = 'Times New Roman'
r_title.font.size = Pt(13.5)
r_title.font.bold = True
r_title.font.color.rgb = BLACK


# Helper for standard academic section headers (No lines, just neat bold text)
def add_heading(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    r.font.name = 'Times New Roman'
    r.font.size = Pt(11.5)
    r.font.bold = True
    r.font.color.rgb = BLACK
    return p


# 1. OBJECTIVES
add_heading('1. Project Objectives')

p_pobj = doc.add_paragraph()
p_pobj.paragraph_format.space_before = Pt(0)
p_pobj.paragraph_format.space_after = Pt(4)
p_pobj.paragraph_format.line_spacing = 1.15
p_pobj.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

r_po_label = p_pobj.add_run('Primary Objective: ')
r_po_label.font.name = 'Times New Roman'
r_po_label.font.size = Pt(10.5)
r_po_label.font.bold = True
r_po_label.font.color.rgb = BLACK

r_po_text = p_pobj.add_run(
    'To develop, evaluate, and deploy an explainable early-warning framework that predicts commercial '
    'bank asset quality distress and regulatory Prompt Corrective Action intervention thresholds 12 to 24 months in advance.'
)
r_po_text.font.name = 'Times New Roman'
r_po_text.font.size = Pt(10.5)
r_po_text.font.color.rgb = DARK

objectives = [
    ('Data Reconstruction: ', 'Reconcile historical RBI statistical archives across bank merger periods into an uninterrupted 21-year macro series and an 87-bank longitudinal panel (649 model-ready observations, 2013–2024).'),
    ('Dynamic Econometric Modeling: ', 'Quantify asset quality persistence and establish the two-year lagged relationship between rapid credit expansion and subsequent bad loans (alpha = 0.5457, beta = +0.0393, p = 0.013).'),
    ('Regulatory Distress Early Warning: ', 'Train gradient-boosted decision trees (XGBoost) to predict statutory RBI Prompt Corrective Action (PCA) Threshold breaches (GNPA >= 6.0%), achieving 76.3% out-of-time accuracy.'),
    ('Explainable AI (TreeSHAP): ', 'Provide transparent, audit-ready risk explanations for supervisory authorities, uncovering non-linear tipping points such as the Return on Assets profitability cliff (RoA < 0.50%).'),
    ('Macro-Stress Testing & Capital Depletion: ', 'Implement logit-bounded satellite projections to simulate economic shocks and quantify bank-by-bank Basel III regulatory capital depletion (CRAR < 9.0%).')
]

for title, desc in objectives:
    bp = doc.add_paragraph(style='List Bullet')
    bp.paragraph_format.space_before = Pt(1.5)
    bp.paragraph_format.space_after = Pt(1.5)
    bp.paragraph_format.line_spacing = 1.12
    bp.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    
    rt = bp.add_run(title)
    rt.font.name = 'Times New Roman'
    rt.font.size = Pt(10)
    rt.font.bold = True
    rt.font.color.rgb = BLACK
    
    rd = bp.add_run(desc)
    rd.font.name = 'Times New Roman'
    rd.font.size = Pt(10)
    rd.font.color.rgb = DARK


# 2. ABSTRACT
add_heading('2. Abstract')

p_abs = doc.add_paragraph()
p_abs.paragraph_format.space_before = Pt(0)
p_abs.paragraph_format.space_after = Pt(6)
p_abs.paragraph_format.line_spacing = 1.15
p_abs.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

r_abs = p_abs.add_run(
    'Accurate early detection of bank asset quality distress is essential for macroprudential regulation and systemic '
    'financial stability. However, supervisory surveillance faces an operational dilemma: classical linear econometric models '
    'provide structural macroeconomic interpretability but fail to capture non-linear default tipping points, whereas complex '
    'machine learning models often operate as uninterpretable black boxes and fail to outperform naive persistence in forecasting '
    'continuous gradual drifts. This paper presents an integrated dual-engine Supervisory Technology (SupTech) early warning '
    'framework evaluated on the Indian Scheduled Commercial Banking sector. First, resolving historical statistical ruptures caused '
    'by public sector bank amalgamations, we reconstruct an uninterrupted 21-year macro panel and synthesize an extensive micro-longitudinal '
    'dataset of 649 bank-year observations spanning 87 commercial banks over 2013–2024. Second, dynamic panel econometric estimation '
    'resolves Nickell endogeneity bias, establishing significant asset quality persistence (alpha = 0.5457, t = 9.13, p < 0.001) and '
    'confirming that credit expansion increases default formation with a two-year lag (beta = +0.0393, p = 0.013). Third, under strict '
    'out-of-time walk-forward validation (Train <= 2021, Test >= 2022), we demonstrate that while persistence dominates continuous point '
    'forecasting, an Extreme Gradient Boosting (XGBoost) classifier decisively outperforms classical logistic regression in predicting '
    'statutory Reserve Bank of India Prompt Corrective Action (PCA) Threshold 1 breaches (GNPA >= 6.0%), achieving an ROC-AUC of 0.710 '
    'versus 0.650 and an accuracy of 76.3% versus 63.5%. Using TreeSHAP explainability, we identify non-linear supervisory thresholds, '
    'revealing an exponential default risk surge when bank Return on Assets drops below 0.50% under elevated credit-deposit leverage. '
    'Finally, we formulate a logit-bounded satellite stress-testing module integrated with a micro-prudential capital adequacy simulation, '
    'projecting post-shock Capital to Risk-Weighted Assets Ratios (CRAR) under adverse macro scenarios. This architecture provides central '
    'banks and commercial lenders with an empirical, transparent, and policy-actionable early warning platform.'
)
r_abs.font.name = 'Times New Roman'
r_abs.font.size = Pt(10)
r_abs.font.color.rgb = DARK


# 3. KEYWORDS
p_kw = doc.add_paragraph()
p_kw.paragraph_format.space_before = Pt(4)
p_kw.paragraph_format.space_after = Pt(0)
p_kw.paragraph_format.line_spacing = 1.15

r_kw_label = p_kw.add_run('Keywords: ')
r_kw_label.font.name = 'Times New Roman'
r_kw_label.font.size = Pt(10)
r_kw_label.font.bold = True
r_kw_label.font.color.rgb = BLACK

r_kw_text = p_kw.add_run(
    'Non-Performing Assets (NPAs), Indian Banking System, Early Warning System (EWS), Explainable AI, '
    'XGBoost, TreeSHAP, Dynamic Panel Econometrics, Prompt Corrective Action (PCA), Macro-Stress Testing, Capital Adequacy (CRAR).'
)
r_kw_text.font.name = 'Times New Roman'
r_kw_text.font.size = Pt(10)
r_kw_text.font.italic = True
r_kw_text.font.color.rgb = DARK

# Save file to both locations
doc.save('Project_Topic_Objectives_and_Abstract.docx')
doc.save('papers/Project_Topic_Objectives_and_Abstract.docx')
print('Successfully generated human-style Word document!')
