import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_SECTION_START
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def build_perfect_ieee_docx():
    doc = Document()

    # -------------------------------------------------------------
    # PAGE SETUP - IEEE Standard Conference Dimensions (Letter)
    # -------------------------------------------------------------
    sec1 = doc.sections[0]
    sec1.page_width = Inches(8.5)
    sec1.page_height = Inches(11.0)
    sec1.top_margin = Inches(0.75)
    sec1.bottom_margin = Inches(1.0)
    sec1.left_margin = Inches(0.625)
    sec1.right_margin = Inches(0.625)
    sec1.header_distance = Inches(0.5)
    sec1.footer_distance = Inches(0.5)

    sectPr1 = sec1._sectPr
    cols1 = sectPr1.xpath('./w:cols')
    if cols1:
        cols1[0].set(qn('w:num'), '1')
    else:
        c = OxmlElement('w:cols')
        c.set(qn('w:num'), '1')
        sectPr1.append(c)

    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Times New Roman'
    normal_style.font.size = Pt(10)
    normal_style.font.color.rgb = RGBColor(0x00, 0x00, 0x00)
    normal_style.paragraph_format.line_spacing = 1.0
    normal_style.paragraph_format.space_before = Pt(0)
    normal_style.paragraph_format.space_after = Pt(0)

    # -------------------------------------------------------------
    # 1. PAPER TITLE (24 pt, Centered, Single Column)
    # -------------------------------------------------------------
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(14)
    r_title = p_title.add_run("Early Warning System for Non-Performing Assets in Indian Commercial Banks: An Explainable Machine Learning and Dynamic Econometric Approach")
    r_title.font.name = 'Times New Roman'
    r_title.font.size = Pt(24)
    r_title.font.color.rgb = RGBColor(0x00, 0x00, 0x00)

    # -------------------------------------------------------------
    # 2. AUTHOR BLOCK (Double-Blind Review Format)
    # -------------------------------------------------------------
    p_auth = doc.add_paragraph()
    p_auth.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_auth.paragraph_format.space_before = Pt(0)
    p_auth.paragraph_format.space_after = Pt(14)
    
    r_auth_name = p_auth.add_run("Author details withheld for double-blind peer review\n")
    r_auth_name.font.name = 'Times New Roman'
    r_auth_name.font.size = Pt(11)
    r_auth_name.font.bold = True
    
    r_auth_affil = p_auth.add_run("Code and data repository link withheld for double-blind review")
    r_auth_affil.font.name = 'Times New Roman'
    r_auth_affil.font.size = Pt(9.5)
    r_auth_affil.font.italic = True

    # -------------------------------------------------------------
    # 3. CONTINUOUS SECTION BREAK -> SECTION 2 (TWO COLUMNS)
    # -------------------------------------------------------------
    sec2 = doc.add_section(WD_SECTION_START.CONTINUOUS)
    sec2.page_width = Inches(8.5)
    sec2.page_height = Inches(11.0)
    sec2.top_margin = Inches(0.75)
    sec2.bottom_margin = Inches(1.0)
    sec2.left_margin = Inches(0.625)
    sec2.right_margin = Inches(0.625)

    sectPr2 = sec2._sectPr
    cols2 = sectPr2.xpath('./w:cols')
    if cols2:
        cols2[0].set(qn('w:num'), '2')
        cols2[0].set(qn('w:space'), '360')
    else:
        c = OxmlElement('w:cols')
        c.set(qn('w:num'), '2')
        c.set(qn('w:space'), '360')
        sectPr2.append(c)

    # -------------------------------------------------------------
    # ABSTRACT & INDEX TERMS
    # -------------------------------------------------------------
    p_abs = doc.add_paragraph()
    p_abs.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_abs.paragraph_format.space_before = Pt(0)
    p_abs.paragraph_format.space_after = Pt(6)
    p_abs.paragraph_format.line_spacing = 1.0
    p_abs.paragraph_format.first_line_indent = Inches(0)
    
    r_abs_lbl = p_abs.add_run("Abstract—")
    r_abs_lbl.font.name = 'Times New Roman'
    r_abs_lbl.font.size = Pt(9)
    r_abs_lbl.font.bold = True
    r_abs_lbl.font.italic = True

    r_abs_body = p_abs.add_run(
        "Non-Performing Assets (NPAs) pose chronic systemic vulnerabilities to financial stability and monetary transmission in emerging market banking systems. "
        "Following the 2015 Asset Quality Review (AQR) by the Reserve Bank of India (RBI), the Indian scheduled commercial banking sector experienced an acute bad-loan accumulation phase, peaking at a Gross NPA (GNPA) ratio of 11.2% in March 2018. "
        "Traditional regulatory surveillance often relies on static linear accounting ratios that omit autoregressive inertia, while modern machine learning models are frequently published without rigorous benchmarking against naive persistence baselines. "
        "In this study, we present a transparent, validation-disciplined Early Warning System (EWS) evaluated across a two-tier RBI dataset: an unbalanced bank-level panel (1,842 raw records across 135 banks over FY2004–FY2025, narrowing to N = 649 model-ready bank-years across 87 entities over FY2013–FY2024) and a sector-aggregate panel restored across FY2013–FY2024 (N = 40 group-years, PSB n = 12). "
        "First, dynamic panel fixed effects (α = 0.519, p < 0.001) and Anderson-Hsiao first-difference IV (α = 0.938, p = 0.003) establish heavy persistence alongside the dominant leading effects of Return on Assets (ROA: -1.780 and -0.993, p < 0.001) and Provision Coverage Ratio (PCR: -0.105 and -0.060, p < 0.05), consistent with the 'bad management' hypothesis. "
        "Second, under strict out-of-time validation (train ≤ 2021, n = 493; test ≥ 2022, n = 156 with 22 breach events), a simple naive persistence baseline (GNPA_t) outperforms Pooled OLS, Fixed Effects, Random Forest, and XGBoost on both continuous MAE (1.74% vs. 2.48%–6.70%) and RMSE (3.41% vs. 3.84%–8.08%), as well as discrete classification for Prompt Corrective Action (PCA) Risk Threshold 1 breaches (GNPA ≥ 6.0% proxy: naive ROC-AUC 0.916 vs. XGBoost 0.907, paired bootstrap p = 0.424). "
        "Third, when current GNPA_t is withheld to isolate forward-looking operational and macro signals, XGBoost achieves a covariate-only ROC-AUC of 0.710 [95% CI: 0.576, 0.822] (vs. Logit 0.650, p = 0.398), and TreeSHAP identifies ROA (mean |SHAP| = 1.125 pp) and lagged credit growth (0.413 pp) as primary leading drivers. "
        "Finally, a linear fixed-effects stress test with 1,000-draw block bootstrap projects PSB GNPAs reaching 6.93% under a COVID-style tail shock (90% CI: [4.80%, 8.05%], 80.7% breach probability) while flagging Small Finance Banks (n = 4) as LOW CONFIDENCE, and a micro-simulation across 65 active 2024 banks shows mean CRAR absorption of 3.27–3.90 pp with zero breaches of the 9.0% minimum floor."
    )
    r_abs_body.font.name = 'Times New Roman'
    r_abs_body.font.size = Pt(9)
    r_abs_body.font.bold = True

    p_kw = doc.add_paragraph()
    p_kw.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_kw.paragraph_format.space_before = Pt(0)
    p_kw.paragraph_format.space_after = Pt(12)
    p_kw.paragraph_format.line_spacing = 1.0
    p_kw.paragraph_format.first_line_indent = Inches(0)

    r_kw_lbl = p_kw.add_run("Index Terms—")
    r_kw_lbl.font.name = 'Times New Roman'
    r_kw_lbl.font.size = Pt(9)
    r_kw_lbl.font.bold = True
    r_kw_lbl.font.italic = True

    r_kw_body = p_kw.add_run("Non-Performing Assets (NPAs), Early Warning Systems, Dynamic Panel Econometrics, Anderson-Hsiao IV, XGBoost, TreeSHAP, Validation Discipline, Prompt Corrective Action, Macroprudential Stress Testing.")
    r_kw_body.font.name = 'Times New Roman'
    r_kw_body.font.size = Pt(9)
    r_kw_body.font.italic = True

    # -------------------------------------------------------------
    # HELPERS
    # -------------------------------------------------------------
    def add_h1(roman, title):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.first_line_indent = Inches(0)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(f"{roman}.   {title.upper()}")
        run.font.name = 'Times New Roman'
        run.font.size = Pt(10)
        run.font.bold = True
        return p

    def add_h2(letter, title):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.first_line_indent = Inches(0)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(f"{letter}.  {title}")
        run.font.name = 'Times New Roman'
        run.font.size = Pt(10)
        run.font.italic = True
        return p

    def add_p(text, indent=True):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.0
        p.paragraph_format.first_line_indent = Inches(0.14) if indent else Inches(0)
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(10)
        return p

    def add_equation_paragraph(runs_spec, eq_num):
        p = doc.add_paragraph()
        p.paragraph_format.tab_stops.add_tab_stop(Inches(1.75), WD_TAB_ALIGNMENT.CENTER)
        p.paragraph_format.tab_stops.add_tab_stop(Inches(3.5), WD_TAB_ALIGNMENT.RIGHT)
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.first_line_indent = Inches(0)

        p.add_run("\t")
        for text, style in runs_spec:
            r = p.add_run(text)
            r.font.name = 'Times New Roman'
            r.font.size = Pt(10)
            if 'i' in style:
                r.font.italic = True
            if 'b' in style:
                r.font.bold = True
            if 'sub' in style:
                r.font.subscript = True
            if 'sup' in style:
                r.font.superscript = True

        p.add_run("\t")
        r_num = p.add_run(f"({eq_num})")
        r_num.font.name = 'Times New Roman'
        r_num.font.size = Pt(10)
        return p

    def add_table_caption(table_num_roman, caption_text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.first_line_indent = Inches(0)
        p.paragraph_format.keep_with_next = True
        
        r1 = p.add_run(f"TABLE {table_num_roman}\n")
        r1.font.name = 'Times New Roman'
        r1.font.size = Pt(8)
        r1.font.bold = True
        
        r2 = p.add_run(caption_text.upper())
        r2.font.name = 'Times New Roman'
        r2.font.size = Pt(8)
        return p

    def style_booktabs_table(table, col_widths):
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        tblPr = table._tbl.tblPr
        borders = parse_xml(
            '<w:tblBorders ' + nsdecls('w') + '>'
            '<w:top w:val="single" w:sz="8" w:space="0" w:color="000000"/>'
            '<w:left w:val="none"/>'
            '<w:bottom w:val="single" w:sz="8" w:space="0" w:color="000000"/>'
            '<w:right w:val="none"/>'
            '<w:insideH w:val="none"/>'
            '<w:insideV w:val="none"/>'
            '</w:tblBorders>'
        )
        tblPr.append(borders)

        for col_idx, width in enumerate(col_widths):
            for row in table.rows:
                row.cells[col_idx].width = width

        for cell in table.rows[0].cells:
            tcPr = cell._tc.get_or_add_tcPr()
            tcBorders = parse_xml(
                '<w:tcBorders ' + nsdecls('w') + '>'
                '<w:bottom w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
                '</w:tcBorders>'
            )
            tcPr.append(tcBorders)

        for row_idx, row in enumerate(table.rows):
            for cell in row.cells:
                p = cell.paragraphs[0]
                p.paragraph_format.space_before = Pt(2)
                p.paragraph_format.space_after = Pt(2)
                p.paragraph_format.line_spacing = 1.0
                p.paragraph_format.first_line_indent = Inches(0)
                for run in p.runs:
                    run.font.name = 'Times New Roman'
                    run.font.size = Pt(7.5)
                    if row_idx == 0:
                        run.font.bold = True

    def add_table_note(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.line_spacing = 1.0
        p.paragraph_format.first_line_indent = Inches(0)
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(7.5)
        run.font.italic = True
        return p

    # -------------------------------------------------------------
    # SECTION I: INTRODUCTION
    # -------------------------------------------------------------
    add_h1("I", "Introduction")
    add_p("The solvency, asset quality, and systemic resilience of commercial banks constitute the foundation of economic expansion and monetary transmission in bank-dominated emerging economies [1], [3]. In India, commercial banks intermediate the vast majority of domestic savings and credit allocation. Between 2011 and 2018, the Indian Scheduled Commercial Banking (SCB) sector endured an acute bad-loan accumulation phase, culminating in a peak Gross Non-Performing Asset (GNPA) ratio of 11.2% in March 2018, sequestering over ₹10.36 lakh crore in impaired advances [1], [3].")
    add_p("The historical origins of this stress were rooted in aggressive debt syndication during the 2004–2008 expansion, when lenders underwrote high-volume loans to infrastructure and industrial projects without commensurate risk buffers [4], [15]. Following regulatory delays and macroeconomic slowdowns, banks utilized restructuring schemes (e.g., Corporate Debt Restructuring and 5:25 refinancing) to postpone loss recognition [1], [15]. In late 2015, the Reserve Bank of India (RBI) initiated its Asset Quality Review (AQR), mandating realistic classification of impaired advances [2], [15], resulting in 11 out of 21 Public Sector Banks (PSBs) entering the Prompt Corrective Action (PCA) framework [1], [2].")
    add_p("This history motivates the development of Supervisory Technology (SupTech) Early Warning Systems (EWS). However, empirical early warning modeling faces two well-documented pitfalls: (1) omitting dynamic state-dependence creates specification error, whereas dynamic fixed-effects OLS suffers from Nickell bias in short panels [5], [6]; and (2) as Beutel et al. [8] demonstrated across European crises, complex machine learning classifiers frequently fail to outperform parsimonious statistical baselines out-of-sample due to overfitting on limited distress episodes. Furthermore, black-box ensembles encounter supervisory skepticism without interpretable attribution [8], [14].")
    add_p("Rather than asserting algorithmic superiority where none exists, this study prioritizes validation discipline and structural transparency across a two-tier RBI dataset: (1) we assemble an unbalanced micro-panel of 87 model-ready banks (N = 649 bank-years over FY2013–FY2024, drawn from 1,842 raw rows across 135 entities over FY2004–FY2025) alongside a restored 4-group sector panel (N = 40 group-years, PSB n = 12); (2) we estimate Static Fixed Effects, Dynamic Fixed Effects (α = 0.519, p < 0.001), and Anderson-Hsiao First-Difference IV (α = 0.938, p = 0.003) [5], proving that Return on Assets (ROA) and Provision Coverage Ratio (PCR) are robust leading signals; (3) we conduct a strictly honest out-of-time benchmark (FY2022–FY2024, n = 156) showing that naive persistence outperforms both linear and tree-based models on continuous error and matches or exceeds full-information ML classifiers (ROC-AUC 0.916 vs. 0.907); (4) we isolate pure forward-looking operational/macro signals via covariate-only XGBoost (AUC 0.710) and TreeSHAP [13], [14]; and (5) we implement a block-bootstrap macro stress test (Table III) paired with bank-level CRAR capital depletion accounting.")

    # -------------------------------------------------------------
    # SECTION II: RELATED WORK & THEORETICAL FOUNDATIONS
    # -------------------------------------------------------------
    add_h1("II", "Related Work & Theoretical Foundations")
    add_h2("A", "Theoretical Models of Bank Asset Quality and Credit Cycles")
    add_p("Berger and DeYoung [4] formulated four core hypotheses linking bank operational efficiency, capitalization, and asset quality: 'bad luck', 'bad management', 'skimping', and 'moral hazard'. Under the 'bad management' hypothesis, operational inefficiencies and deficient credit appraisal Granger-cause subsequent surges in problem loans. Under 'moral hazard', thinly capitalized institutions underwrite high-variance credit under implicit sovereign guarantees [1], [4]. Cross-country studies by Louzis et al. [10], Messai and Jouini [9], and Ari, Chen, and Ratnovski [7] corroborate that non-performing loans exhibit strong autoregressive persistence and recover slowly after systemic shocks, driven jointly by GDP slowdowns, interest rate tightening, and profitability erosion.")

    add_h2("B", "The Indian Banking NPA Crisis: Institutional Drivers")
    add_p("Acharya [1] and Rajan [15] documented that impaired advances during the 2015–2018 cycle were heavily concentrated in Public Sector Banks, driven by infrastructure concentration, weak project diligence, and extended forbearance. Mishra et al. [11] confirmed high autoregressive persistence and macroeconomic cyclicality in Indian banking panels using dynamic estimators. To codify intervention triggers, the RBI issued its Revised Prompt Corrective Action (PCA) Framework [2], establishing mandatory thresholds on capital adequacy, leverage, and asset quality.")

    add_h2("C", "Evolution and Validation Discipline in Supervisory EWS")
    add_p("Early warning frameworks span static probits [4], [9], dynamic panel estimators [5], [6], and regularized machine learning [12]. Crucially, Beutel, List, and von Schweinitz [8] evaluated early warning models across 15 European economies and showed that standard logit models frequently outperform or match machine learning out-of-sample because tree ensembles overfit noisy crisis thresholds. To make tree ensembles inspectable, Lundberg and Lee [13] unified Shapley Additive Explanations (SHAP) and Lundberg et al. [14] derived polynomial-time TreeSHAP, enabling exact additive attribution of non-linear predictions.")

    # -------------------------------------------------------------
    # SECTION III: DATA RECONSTRUCTION & TWO-TIER PANEL ARCHITECTURE
    # -------------------------------------------------------------
    add_h1("III", "Data Architecture & Forensic Reconciliation")
    add_p("Our empirical pipeline integrates two complementary datasets constructed directly from official RBI Statistical Tables Relating to Banks in India (F4 Gross NPAs, F5 Key Ratios, F7 NPA Movements) and the Database on Indian Economy (DBIE) [3]:")
    add_p("1) Tier 1: Bank-Level Micro-Panel: Raw extraction across FY2004–FY2025 captures 1,842 unbalanced bank-year records spanning 135 distinct banks (reflecting post-2016 Small Finance Bank licensing and the 2017–2020 PSB mergers, where pre-2017 SBI associates remain separate reporting entities). Requiring non-missing values for two-year lagged credit growth, Provision Coverage Ratio (which begins in RBI's F7 tables in FY2013), and the 1-year ahead target narrows the model-ready panel to FY2013–FY2024, comprising N = 649 bank-years across 87 unique entities: Private Sector Banks (233 obs, 23 banks), Public Sector Banks (218 obs, 26 banks), Foreign Banks (167 obs, 29 banks), and Small Finance Banks (31 obs, 10 banks; IDBI Bank transitions from PSB to Private in FY2019 per RBI classification).")
    add_p("2) Tier 2: Restored Macro Bank-Group Panel: To conduct group-level macro stress testing without reporting breaks, aggregate annual totals from FY2004–FY2025 (74 group-years) restore the pre-2018 PSB series by summing 'State Bank of India & Associates' and 'Nationalised Banks' prior to RBI's 2018 unified 'Public Sector Banks' category. After covariate and target alignment over FY2013–FY2024, this Tier 2 panel provides N = 40 model-ready observations: PSB (n = 12), Private (n = 12), Foreign (n = 12), and SFB (n = 4, licensed from 2016 onward and therefore flagged LOW CONFIDENCE under our n < 8 reliability rule).")

    # -------------------------------------------------------------
    # SECTION IV: SYSTEM METHODOLOGY & MATHEMATICAL FORMULATION
    # -------------------------------------------------------------
    add_h1("IV", "System Methodology & Mathematical Formulation")
    add_h2("A", "Static, Dynamic Fixed Effects, and Anderson-Hsiao FD-IV Models")
    add_p("Under a static fixed-effects panel model, asset quality is formulated as:")
    add_equation_paragraph([
        ("GNPA", "i"), ("i,t", "sub"), (" = ", ""), ("α", "i"), ("0", "sub"), (" + ", ""),
        ("X", "b"), ("i,t", "sub"), ("⊤", "sup"), (" ", ""), ("β", "b"), (" + ", ""),
        ("μ", "i"), ("i", "sub"), (" + ", ""), ("ε", "i"), ("i,t", "sub")
    ], "1")
    add_p("where μ_i denotes time-invariant bank fixed effects. Incorporating one-year autoregressive persistence yields the Dynamic Fixed Effects (LSDV) specification:")
    add_equation_paragraph([
        ("GNPA", "i"), ("i,t", "sub"), (" = ", ""), ("α", "i"), (" ", ""), ("GNPA", "i"), ("i,t-1", "sub"),
        (" + ", ""), ("X", "b"), ("i,t", "sub"), ("⊤", "sup"), (" ", ""), ("β", "b"), (" + ", ""),
        ("μ", "i"), ("i", "sub"), (" + ", ""), ("ε", "i"), ("i,t", "sub")
    ], "2")
    add_p("Because LSDV suffers from downward Nickell bias in short panels [5], we also estimate the Anderson-Hsiao First-Difference Instrumental Variable (FD-IV) estimator via 2SLS on consecutive-year differences:")
    add_equation_paragraph([
        ("Δ", ""), ("GNPA", "i"), ("i,t", "sub"), (" = ", ""), ("α", "i"), (" ", ""),
        ("Δ", ""), ("GNPA", "i"), ("i,t-1", "sub"), (" + ", ""),
        ("Δ", ""), ("X", "b"), ("i,t", "sub"), ("⊤", "sup"), (" ", ""), ("β", "b"), (" + ", ""),
        ("Δ", ""), ("ε", "i"), ("i,t", "sub")
    ], "3")
    add_p("using the twice-lagged level GNPA_{i,t-2} as an excluded instrument satisfying:")
    add_equation_paragraph([
        ("𝔼[ ", ""), ("GNPA", "i"), ("i,t-2", "sub"), (" · ", ""), ("Δ", ""), ("ε", "i"), ("i,t", "sub"), (" ] = 0", "")
    ], "4")

    add_h2("B", "Machine Learning Classification & Regularization (XGBoost)")
    add_p("Under RBI Circular RBI/2021-22/118 [2], the statutory PCA Risk Threshold 1 trigger is Net NPA ≥ 6.0%. Because offsite gross asset monitoring precedes provisioning offsets, we construct a binary gross-NPA distress proxy target (GNPA ≥ 6.0% proxy):")
    add_equation_paragraph([
        ("Y", "i"), ("i,t+1", "sub"), ("PCA", "sup"), (" = ", ""), ("𝕀( ", ""),
        ("GNPA", "i"), ("i,t+1", "sub"), (" ≥ 6.0% )", "")
    ], "5")
    add_p("We deploy Extreme Gradient Boosting (XGBoost) [12], minimizing a regularized empirical loss over M additive trees:")
    add_equation_paragraph([
        ("ℒ", "i"), ("(m)", "sup"), (" = ", ""), ("∑", ""), ("k=1", "sub"), ("K", "sup"),
        (" l( ", ""), ("y", "i"), ("k", "sub"), (", ", ""), ("ŷ", "i"), ("k", "sub"), ("(m-1)", "sup"),
        (" + ", ""), ("f", "i"), ("m", "sub"), ("( ", ""), ("x", "b"), ("k", "sub"), (" ) ) + ", ""),
        ("Ω( ", ""), ("f", "i"), ("m", "sub"), (" )", "")
    ], "6")
    add_equation_paragraph([
        ("Ω( ", ""), ("f", "i"), ("m", "sub"), (" ) = ", ""), ("γ", "i"), (" ", ""), ("T", "i"), ("m", "sub"),
        (" + ½ ", ""), ("λ", "i"), (" ", ""), ("∑", ""), ("j=1", "sub"), ("Tm", "sup"),
        ("w", "i"), ("j", "sub"), ("2", "sup"), (" + ", ""), ("α", "i"), ("reg", "sub"), (" ", ""),
        ("∑", ""), ("j=1", "sub"), ("Tm", "sup"), ("| ", ""), ("w", "i"), ("j", "sub"), (" |", "")
    ], "7")
    add_p("To prevent apples-to-oranges benchmarking, we evaluate both Regime A (operational/macro covariates excluding GNPA_t, matching our Shapley driver model) and Regime B (full information including GNPA_t) against Naive Persistence (GNPA_t ≥ 6.0%).")

    add_h2("C", "Game-Theoretic Explainability via TreeSHAP")
    add_p("To make non-linear tree classifications auditable [13], [14], TreeSHAP assigns exact additive attributions ϕ_j satisfying local efficiency:")
    add_equation_paragraph([
        ("ϕ", "i"), ("j", "sub"), ("( ", ""), ("f", "i"), (", ", ""), ("x", "b"), (" ) = ", ""),
        ("∑", ""), ("S ⊆ F \\ {j}", "sub"),
        (" [ |S|! (|F| - |S| - 1)! / |F|! ] · [ f(S ∪ {j}) - f(S) ]", "")
    ], "8")
    add_equation_paragraph([
        ("f( ", ""), ("x", "b"), (" ) = ", ""), ("ϕ", "i"), ("0", "sub"), ("( ", ""), ("f", "i"), (" ) + ", ""),
        ("∑", ""), ("j=1", "sub"), ("|F|", "sup"), ("ϕ", "i"), ("j", "sub"), ("( ", ""), ("f", "i"), (", ", ""), ("x", "b"), (" )", "")
    ], "9")

    add_h2("D", "Fixed-Effects Stress Test, Block Bootstrap & Capital Depletion")
    add_p("Using the restored Tier 2 bank-group Fixed Effects model (β_FE), scenario shocks ΔX^{shock} map directly to projected group GNPAs from FY2024 baselines:")
    add_equation_paragraph([
        ("GNPA", "i"), ("g", "sub"), ("stressed", "sup"), (" = max( 0, ", ""),
        ("GNPA", "i"), ("g,2024", "sub"), (" + ", ""), ("Δ", ""), ("X", "b"), ("shock", "sup"), (" ", ""), ("β̂", "b"), ("FE", "sub"), (" )", "")
    ], "10")
    add_p("Sampling uncertainty is quantified via a 1,000-draw within-group block bootstrap resampling annual observations per cohort and refitting β̂_FE. To link aggregate stress to micro-solvency across individual banks active in FY2024 (n = 65 with complete CRAR and GNPA), we compute incremental provisioning and post-shock Capital to Risk-Weighted Assets Ratios (CRAR) assuming standard Basel risk-density approximation RWA_i ≈ 0.70 × A_{i,2024} (applying a 70% regulatory PCR fallback for 8 entities missing FY2024 NPA movement entries):")
    add_equation_paragraph([
        ("Δ", ""), ("Prov", "i"), ("i", "sub"), (" = ( ", ""), ("Δ", ""), ("GNPA", "i"), ("shock", "sub"),
        (" / 100 ) × ", ""), ("A", "i"), ("i,2024", "sub"), (" × ", ""), ("PCR", "i"), ("i,2024", "sub")
    ], "11")
    add_equation_paragraph([
        ("CRAR", "i"), ("i", "sub"), ("post", "sup"), (" = max( 0, ", ""),
        ("CRAR", "i"), ("i", "sub"), ("pre", "sup"), (" - [ ", ""),
        ("Δ", ""), ("Prov", "i"), ("i", "sub"), (" / (0.70 × ", ""), ("A", "i"), ("i,2024", "sub"), (" ) ] × 100 )", "")
    ], "12")

    # -------------------------------------------------------------
    # SECTION V: EMPIRICAL RESULTS & DISCUSSION
    # -------------------------------------------------------------
    add_h1("V", "Empirical Results & Discussion")
    add_h2("A", "Econometric Estimation Findings")
    add_p("Table I reports all three panel estimators on Tier 1 data. Lagged GNPA exhibits significant persistence under Dynamic FE (α = 0.519, p < 0.001) and rises to α = 0.938 (p = 0.003) under Anderson-Hsiao FD-IV once downward Nickell bias is corrected [5]. Crucially, across all three specifications, higher Return on Assets significantly lowers future NPAs (-2.564, -1.780, and -0.993; all p < 0.001), and higher Provision Coverage Ratios significantly dampen subsequent GNPA (-0.105, p = 0.045 in Dynamic FE; -0.060, p = 0.002 in FD-IV). This provides robust support for Berger and DeYoung's [4] 'bad management' mechanism.")

    # Table I
    add_table_caption("I", "Bank-Level Econometric Estimators (Tier 1 Micro-Panel)")
    tbl1 = doc.add_table(rows=8, cols=4)
    tbl1_widths = [Inches(1.15), Inches(0.78), Inches(0.78), Inches(0.78)]
    
    headers1 = ["Variable", "Static FE", "Dynamic FE", "Anderson-Hsiao FD-IV"]
    for c_idx, h in enumerate(headers1):
        tbl1.rows[0].cells[c_idx].paragraphs[0].text = h

    t1_data = [
        ["Lagged GNPA (α)", "---", "0.519*** (0.070)", "0.938*** (0.313)"],
        ["Return on Assets", "-2.564*** (0.396)", "-1.780*** (0.350)", "-0.993*** (0.269)"],
        ["Credit Growth (t-2)", "-0.019** (0.009)", "0.011 (0.009)", "0.021 (0.014)"],
        ["CD Ratio", "-0.004*** (0.000)", "-0.062 (0.061)", "-0.002 (0.018)"],
        ["PCR (%)", "-0.051 (0.038)", "-0.105** (0.052)", "-0.060*** (0.020)"],
        ["GDP Growth (%)", "0.071 (0.064)", "0.112* (0.068)", "0.035 (0.036)"],
        ["Policy Repo (%)", "-0.949*** (0.341)", "-0.517* (0.300)", "-0.375* (0.226)"]
    ]
    for r_idx, row in enumerate(t1_data):
        for c_idx, val in enumerate(row):
            tbl1.rows[r_idx+1].cells[c_idx].paragraphs[0].text = val
    style_booktabs_table(tbl1, tbl1_widths)
    add_table_note("* p < 0.10, ** p < 0.05, *** p < 0.01. Entity-clustered standard errors in parentheses. Static FE: N = 649 (87 banks, Within R² = 0.341). Dynamic FE: N = 562 (83 banks, Within R² = 0.443). FD-IV2SLS (consecutive differenced years): N = 456 (72 banks, R² = -0.293). Note: Static FE CD-ratio significance reflects one foreign-branch leverage outlier (JSC VTB Bank, FY2016, 10,994%); excluding it yields -0.057 (p = 0.311), consistent with Dynamic FE.")

    add_h2("B", "Out-of-Time Predictive Performance & Validation Discipline")
    add_p("Training exclusively up to FY2021 (n = 493) and testing out-of-time on FY2022–FY2024 (n = 156, containing 22 breach events: 18 continuing from t, 4 new onsets, and 21 recoveries) yields a sobering validation finding (Table II). First, on continuous level forecasting, Naive Persistence (GNPA_t) achieves MAE = 1.74%, RMSE = 3.41%, and R² = 0.213—beating every parametric and tree model on BOTH MAE and RMSE, even when GNPA_t is supplied in Regime B (XGBoost+GNPA_t: MAE 2.48%, RMSE 3.84%; Pooled OLS+GNPA_t: MAE 2.70%, RMSE 4.16%). Without GNPA_t (Regime A), linear models extrapolate poorly (Pooled OLS MAE 6.42%, RMSE 7.78%; Panel FE MAE 6.70%, RMSE 8.08%).")
    add_p("Second, on discrete PCA-proxy breach classification (Table II), a naive persistence classifier (flagging GNPA_t ≥ 6.0%, ranked by GNPA_t) achieves ROC-AUC = 0.916 [95% CI: 0.829, 0.982], Accuracy = 84.0%, Precision = 46.2%, Recall = 81.8% (18/22), and F1 = 0.590. Full-information XGBoost+GNPA_t reaches ROC-AUC = 0.907 [0.813, 0.982] and Accuracy = 82.1%—statistically indistinguishable from naive persistence (paired bootstrap p = 0.424). Only when GNPA_t is intentionally withheld (Regime A) to isolate forward operational/macro risk signals does XGBoost achieve non-trivial ranking power (ROC-AUC = 0.710 [0.576, 0.822], Accuracy = 76.3%), though its advantage over Logit (0.650) is not statistically significant (p = 0.398). This directly confirms Beutel et al.'s [8] caution against overclaiming ML gains over parsimonious persistence rules.")

    # Table II
    add_table_caption("II", "Out-of-Time Test Benchmarks (FY2022–FY2024, N = 156, 22 Breaches)")
    tbl2 = doc.add_table(rows=8, cols=6)
    tbl2_widths = [Inches(1.1), Inches(0.42), Inches(0.45), Inches(0.65), Inches(0.42), Inches(0.45)]

    headers2 = ["Model (Feature Set)", "MAE", "RMSE", "AUC [95% CI]", "Acc.", "Rec."]
    for c_idx, h in enumerate(headers2):
        tbl2.rows[0].cells[c_idx].paragraphs[0].text = h

    t2_data = [
        ["Naive Persistence (GNPA_t)", "1.74%", "3.41%", "0.916 [0.83,0.98]", "84.0%", "81.8%"],
        ["Reg. A (No GNPA_t): Logit/OLS", "6.42%", "7.78%", "0.650 [0.47,0.81]", "63.5%", "68.2%"],
        ["Reg. A (No GNPA_t): Rand. For.", "3.15%", "4.49%", "0.692 [0.55,0.81]", "71.2%", "54.5%"],
        ["Reg. A (No GNPA_t): XGBoost", "3.22%", "4.45%", "0.710 [0.58,0.82]", "76.3%", "50.0%"],
        ["Reg. B (+GNPA_t): Logit/OLS", "2.70%", "4.16%", "0.872 [0.76,0.96]", "76.9%", "81.8%"],
        ["Reg. B (+GNPA_t): Rand. For.", "2.96%", "4.12%", "0.868 [0.75,0.96]", "80.8%", "86.4%"],
        ["Reg. B (+GNPA_t): XGBoost", "2.48%", "3.84%", "0.907 [0.81,0.98]", "82.1%", "81.8%"]
    ]
    for r_idx, row in enumerate(t2_data):
        for c_idx, val in enumerate(row):
            tbl2.rows[r_idx+1].cells[c_idx].paragraphs[0].text = val
    style_booktabs_table(tbl2, tbl2_widths)
    add_table_note("All models evaluated on identical N = 156 test observations (22 breaches). Reg. A OLS row pairs Pooled OLS regression (MAE/RMSE) with Logistic Regression classification. Paired bootstrap p-values: Reg. A XGBoost vs. Logit p = 0.398; Naive vs. Reg. B XGBoost p = 0.424. Panel FE (Reg. A) gives MAE 6.70%, RMSE 8.08%.")

    add_h2("C", "TreeSHAP Game-Theoretic Attribution")
    add_p("On the Regime A covariate-only classifier, global TreeSHAP feature importances [13], [14] confirm that forward distress is primarily explained by Return on Assets (mean |SHAP| = 1.125 pp), followed by two-year lagged credit growth (0.413 pp), GDP growth (0.404 pp), Provision Coverage Ratio (0.316 pp), Credit-Deposit ratio (0.254 pp), policy repo rate (0.075 pp), and CPI inflation (0.032 pp). By comparison, on the aggregate 4-group panel (N = 40), ROA also ranks first at 1.454 pp (followed by PCR at 0.709 pp). Both micro and macro evidence independently establish profitability compression as the earliest measurable precursor of asset impairment.")

    add_h2("D", "Macroeconomic Stress Testing & Bank Capital Depletion")
    add_p("Table III reports the Tier 2 Fixed Effects stress projections (Within R² = 0.665, N = 40; ROA coef = -3.414) calibrated to historical RBI stress shocks. Under the COVID-FY21 Tail Risk scenario (GDP -3.0 pp, repo +200 bps, credit growth -6.0 pp, ROA -0.8 pp; composite +3.46 pp GNPA impact), PSB point-estimate GNPA rises from 3.47% to 6.93% (bootstrap mean 6.68%, 90% CI: [4.80%, 8.05%], 80.7% breach probability). Crucially, restoring pre-2018 PSB history yields n = 12 reliable observations for PSBs, Private, and Foreign banks, leaving only Small Finance Banks (n = 4, tail risk 5.89%, 90% CI: [3.76%, 7.01%]) flagged as LOW CONFIDENCE.")
    add_p("Translating the +3.46 pp Tail Risk GNPA shock to individual FY2024 balance sheets across all 65 active banks with complete CRAR data (12 PSBs, 21 Private, 20 Foreign, 12 SFBs) via Eqs. (11)–(12) indicates mean CRAR absorption of 3.90 pp for PSBs (16.42% to 12.52%), 3.49 pp for Private banks (18.20% to 14.71%), 3.60 pp for Foreign banks (34.63% to 31.03%), and 3.27 pp for SFBs (23.41% to 20.14%), with zero banks breaching the 9.0% statutory CRAR minimum due to strengthened post-2021 capital buffers.")

    # Table III
    add_table_caption("III", "Restored Group Stress Projections & Tail Uncertainty (Tier 2, N = 40)")
    tbl3 = doc.add_table(rows=5, cols=6)
    tbl3_widths = [Inches(0.55), Inches(0.50), Inches(0.50), Inches(0.50), Inches(0.80), Inches(0.65)]

    headers3 = ["Group", "Base '24", "Severe", "Tail Risk", "90% CI (Breach%)", "Confidence"]
    for c_idx, h in enumerate(headers3):
        tbl3.rows[0].cells[c_idx].paragraphs[0].text = h

    t3_data = [
        ["Foreign", "1.19%", "3.24%", "4.65%", "[2.52, 5.77] (2.9%)", "reliable (n=12)"],
        ["Private", "1.85%", "3.90%", "5.31%", "[3.18, 6.43] (12.5%)", "reliable (n=12)"],
        ["PSB", "3.47%", "5.52%", "6.93%", "[4.80, 8.05] (80.7%)", "reliable (n=12)"],
        ["SFB", "2.43%", "4.48%", "5.89%", "[3.76, 7.01] (38.7%)", "LOW (n=4)"]
    ]
    for r_idx, row in enumerate(t3_data):
        for c_idx, val in enumerate(row):
            tbl3.rows[r_idx+1].cells[c_idx].paragraphs[0].text = val
    style_booktabs_table(tbl3, tbl3_widths)
    add_table_note("Point estimates from run_stress_test on restored banking_panel.csv (N=40); 90% CIs and PCA breach probabilities (>6.0%) from 1,000 block-bootstrap draws. Groups with n < 8 flagged LOW CONFIDENCE.")

    # -------------------------------------------------------------
    # SECTION VI: SUPERVISORY LIMITATIONS & POLICY IMPLICATIONS
    # -------------------------------------------------------------
    add_h1("VI", "Limitations & Policy Implications")
    add_p("Three methodological limitations govern interpretation: (1) The out-of-time test partition contains 156 bank-years with 22 breach events (only 4 new onsets), yielding wide confidence intervals and favoring simple persistence; (2) Our classification target uses GNPA ≥ 6.0% as a gross proxy for the statutory Net-NPA PCA trigger [2]; and (3) Group-level stress elasticities rest on N = 40 observations, where SFBs (n = 4) carry substantial small-sample uncertainty.")
    add_p("For supervisory policy, our results support three disciplined practices: (1) Mandatory Naive Benchmarking: SupTech classifiers should never be deployed without demonstrating superiority over persistence (GNPA_t) out-of-sample; (2) Profitability-Led Surveillance: Because ROA dominates both dynamic panel regressions and TreeSHAP rankings, offsite monitoring should flag profitability erosion 12–24 months ahead of asset deterioration; and (3) Uncertainty-Aware Stress Testing: Scenario projections must publish bootstrap intervals and explicit sample-size flags.")

    # -------------------------------------------------------------
    # SECTION VII: CONCLUSION
    # -------------------------------------------------------------
    add_h1("VII", "Conclusion")
    add_p("This study presented a reproducible, validation-disciplined Early Warning System for Indian commercial banks built across a two-tier RBI dataset (N = 649 bank-level observations across 87 entities and N = 40 restored bank-group observations). Dynamic Fixed Effects (α = 0.519) and Anderson-Hsiao FD-IV (α = 0.938) confirm heavy credit inertia alongside the leading causal roles of ROA and PCR. Crucially, honest out-of-time testing shows that naive persistence outperforms both linear and machine learning models on continuous error (MAE 1.74%, RMSE 3.41%) and matches full-information XGBoost on PCA breach detection (AUC 0.916 vs. 0.907, p = 0.424). Consequently, the core regulatory value of explainable ML and dynamic econometrics lies in forward driver identification (TreeSHAP ROA = 1.125 pp) and uncertainty-quantified macro stress testing.")

    # -------------------------------------------------------------
    # SECTION VIII: REFERENCES (Strictly 15 verified references)
    # -------------------------------------------------------------
    add_h1("VIII", "References")
    
    references_data = [
        "[1] V. V. Acharya, Quest for Restoring Financial Stability in India. New Delhi, India: SAGE Publications, 2020.",
        "[2] Reserve Bank of India, \"Prompt Corrective Action (PCA) framework for scheduled commercial banks,\" RBI Circular RBI/2021-22/118, DOS.CO.PPG.SEC.No.4/11.01.005/2021-22, Nov. 2, 2021.",
        "[3] Reserve Bank of India, Report on Trend and Progress of Banking in India 2023-24, Reserve Bank of India, Mumbai, India, Dec. 2024.",
        "[4] A. N. Berger and R. DeYoung, \"Problem loans and cost efficiency in commercial banks,\" Journal of Banking & Finance, vol. 21, no. 6, pp. 849–870, Jun. 1997.",
        "[5] M. Arellano and S. Bond, \"Some tests of specification for panel data: Monte Carlo evidence and an application to employment equations,\" The Review of Economic Studies, vol. 58, no. 2, pp. 277–297, Apr. 1991.",
        "[6] R. Blundell and S. Bond, \"Initial conditions and moment restrictions in dynamic panel data models,\" Journal of Econometrics, vol. 87, no. 1, pp. 115–143, Aug. 1998.",
        "[7] A. Ari, S. Chen, and L. Ratnovski, \"The dynamics of non-performing loans during banking crises: A new database,\" European Central Bank Working Paper Series, no. 2395, Apr. 2020.",
        "[8] J. Beutel, S. List, and G. von Schweinitz, \"Does machine learning help us predict banking crises?,\" Journal of Financial Stability, vol. 45, Art. no. 100693, Dec. 2019, doi: 10.1016/j.jfs.2019.100693.",
        "[9] A. S. Messai and F. Jouini, \"Micro and macro determinants of non-performing loans,\" International Journal of Economics and Financial Issues, vol. 3, no. 4, pp. 852–860, 2013.",
        "[10] D. P. Louzis, A. T. Vouldis, and V. L. Metaxas, \"Macroeconomic and bank-specific determinants of non-performing loans in Greece: A comparative study of mortgage, business and consumer loan portfolios,\" Journal of Banking & Finance, vol. 36, no. 4, pp. 1012–1027, Apr. 2012.",
        "[11] A. K. Mishra, S. Jain, and M. Abid, \"Non-performing assets and its determinants in the Indian banking system: An empirical analysis using dynamic panel data models,\" International Journal of Finance & Economics, vol. 26, no. 4, pp. 5948–5962, Oct. 2021.",
        "[12] T. Chen and C. Guestrin, \"XGBoost: A scalable tree boosting system,\" in Proc. 22nd ACM SIGKDD Int. Conf. Knowledge Discovery and Data Mining (KDD '16), San Francisco, CA, USA, 2016, pp. 785–794.",
        "[13] S. M. Lundberg and S.-I. Lee, \"A unified approach to interpreting model predictions,\" in Advances in Neural Information Processing Systems (NeurIPS 2017), Long Beach, CA, USA, 2017, pp. 4765–4774.",
        "[14] S. M. Lundberg, G. Erion, H. Chen, A. DeGrave, J. M. Prutkin, B. Nair, R. Katz, and S.-I. Lee, \"From local explanations to global understanding with explainable AI for trees,\" Nature Machine Intelligence, vol. 2, no. 1, pp. 56–67, Jan. 2020.",
        "[15] R. G. Rajan, \"Note to the Parliamentary Estimates Committee on Bank NPAs,\" Parliament of India, New Delhi, India, Sep. 2018."
    ]

    for ref in references_data:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.0
        p.paragraph_format.left_indent = Inches(0.25)
        p.paragraph_format.first_line_indent = Inches(-0.25)

        run = p.add_run(ref)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(8)

    output_path = os.path.abspath("papers/IEEE_NPA_EWS_Research_Paper.docx")
    doc.save(output_path)
    print(f"Strict IEEE Conference Document successfully built and saved to {output_path}")

if __name__ == "__main__":
    build_perfect_ieee_docx()
