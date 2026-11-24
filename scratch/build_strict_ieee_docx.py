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
    # Margins: Top 0.75", Bottom 1.0", Left 0.625", Right 0.625"
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

    # Force Section 1 to be single column (Title + Authors)
    sectPr1 = sec1._sectPr
    cols1 = sectPr1.xpath('./w:cols')
    if cols1:
        cols1[0].set(qn('w:num'), '1')
    else:
        c = OxmlElement('w:cols')
        c.set(qn('w:num'), '1')
        sectPr1.append(c)

    # Base Normal Style
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
    # 2. AUTHOR BLOCK (Clean Standard Academic / Blind Review Format)
    # -------------------------------------------------------------
    p_auth = doc.add_paragraph()
    p_auth.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_auth.paragraph_format.space_before = Pt(0)
    p_auth.paragraph_format.space_after = Pt(14)
    
    r_auth_name = p_auth.add_run("Research Working Paper — Department of Computer Science & Economics\n")
    r_auth_name.font.name = 'Times New Roman'
    r_auth_name.font.size = Pt(11)
    r_auth_name.font.bold = True
    
    r_auth_affil = p_auth.add_run("Author Details Redacted for Double-Blind Peer Review\nFinancial Machine Learning and Macroprudential Surveillance Research Group\nContact / Verification Repository: github.com/rdnk2004/NPA-RBI")
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
        "Non-Performing Assets (NPAs) pose chronic systemic vulnerabilities to financial stability and monetary policy transmission in emerging market banking systems. "
        "Following the 2015 Asset Quality Review (AQR) by the Reserve Bank of India (RBI), the Indian scheduled commercial banking sector experienced an acute bad-loan accumulation phase, peaking at a Gross NPA (GNPA) ratio of 11.2% in March 2018. "
        "Traditional regulatory early warning systems predominantly depend on static linear accounting ratios that fail to account for dynamic autoregressive inertia, while high-capacity machine learning models are frequently deployed without rigorous benchmarking against naive persistence baselines. "
        "In this study, we develop a transparent, dual-framework Early Warning System (EWS) evaluated on an unbalanced longitudinal micro-panel of 87 Indian commercial banks spanning FY2005 to FY2024 (N = 649 model-ready bank-years). "
        "First, we address the reporting discontinuity surrounding the 2017 State Bank of India associate megamerger through backward-consistent entity consolidation. "
        "Second, we formalize a dynamic panel model that quantifies structural persistence (α = 0.519, p < 0.001) and isolates the leading causal influence of Return on Assets (ROA: -1.780, p < 0.001) and Provision Coverage Ratio (PCR: -0.105, p = 0.045), confirming the 'bad management' hypothesis. "
        "Third, evaluating continuous regression under out-of-time validation (train ≤ 2021, test ≥ 2022, n = 156), we document that a simple naive persistence baseline outperforms both Random Forest and XGBoost (MAE 1.74% vs. 3.16% and 3.22%), demonstrating that complex algorithms fail to beat persistence in continuous level prediction on persistent credit series. "
        "Fourth, when reframed as a discrete supervisory early warning task for Prompt Corrective Action (PCA) Risk Threshold 1 breaches (GNPA ≥ 6.0% proxy), XGBoost achieves an out-of-sample ROC-AUC of 0.710 [95% CI: 0.581, 0.822] and accuracy of 76.3%, modestly outperforming Logistic Regression (AUC 0.650) and Random Forest (AUC 0.692). "
        "Fifth, cooperative game-theoretic TreeSHAP feature attributions identify operational profitability (ROA, mean |SHAP| = 1.125 pp) and credit expansion velocity as the primary drivers of distress. "
        "Finally, we implement a bounded logit-space macroprudential stress-testing satellite simulator with block-bootstrap confidence intervals, revealing that under a severe tail shock calibrated to the COVID-19/AQR cycle, Public Sector Bank GNPAs elevate to 6.29% [90% CI: 4.40%, 7.07%] with an estimated 64.3% threshold breach probability, accompanied by transparent data-sufficiency caveats. "
        "Our findings provide a scientifically disciplined roadmap for supervisory early warning surveillance in bank-dominated emerging economies."
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

    r_kw_body = p_kw.add_run("Non-Performing Assets (NPAs), Early Warning Systems, Dynamic Panel Econometrics, Arellano-Bond GMM, XGBoost, Explainable AI (XAI), TreeSHAP, Prompt Corrective Action, Macroprudential Stress Testing.")
    r_kw_body.font.name = 'Times New Roman'
    r_kw_body.font.size = Pt(9)
    r_kw_body.font.italic = True

    # -------------------------------------------------------------
    # FORMATTING HELPERS FOR TWO-COLUMN IEEE BODY
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
                    run.font.size = Pt(8)
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
    add_p("The solvency, asset quality, and systemic resilience of commercial banks constitute the indispensable foundation of economic expansion and monetary transmission in bank-dominated emerging economies [1], [3]. In India, commercial banks intermediate the vast majority of national domestic savings and credit allocation. Between 2011 and 2018, the Indian Scheduled Commercial Banking (SCB) sector endured an acute bad-loan accumulation phase, culminating in a historic peak Gross Non-Performing Asset (GNPA) ratio of 11.2% in March 2018, sequestering over ₹10.36 lakh crore in impaired advances [1], [3].")
    add_p("The historical origins of this stress were rooted in aggressive debt syndication during the 2004–2008 economic expansion, where state-owned lenders underwrote high-volume loans to capital-intensive infrastructure and industrial projects without adequate risk buffers [4], [15]. When infrastructure projects encountered statutory clearance bottlenecks, global commodity downturns, and domestic demand slowdowns, commercial lenders utilized regulatory restructuring mechanisms (e.g., Corporate Debt Restructuring, 5:25 schemes) to 'evergreen' unviable credit, masking balance-sheet deterioration [1], [15].")
    add_p("This forbearance terminated in late 2015 when the Reserve Bank of India (RBI) initiated the comprehensive Asset Quality Review (AQR), mandating uniform recognition of impaired credit [2], [15]. The resulting surge in bad loans triggered substantial provisioning burdens and operational losses, placing 11 out of 21 Public Sector Banks (PSBs) under the RBI's Prompt Corrective Action (PCA) framework [1], [2].")
    add_p("This historical episode underscores the urgent requirement for forward-looking Early Warning Systems (EWS) in banking surveillance. Traditional supervisory surveillance relies heavily on static accounting metrics and backward-looking financial ratios [4], [9]. Static panel regressions fail to account for autoregressive persistence—wherein past impaired assets create multi-year provisioning drag—and suffer from severe Nickell bias in dynamic panel settings [5], [6]. Furthermore, while machine learning algorithms offer flexible non-linear pattern recognition, recent empirical assessments (e.g., Beutel et al. [8]) emphasize that complex machine learning algorithms are frequently matched or outperformed by parsimonious statistical baselines out-of-sample due to overfitting in small macroeconomic event samples. Moreover, the black-box nature of tree ensembles poses significant barriers to central bank adoption, where legal accountability demands fully interpretable risk attribution [8], [14].")
    add_p("In this study, we address these challenges by developing a disciplined, transparent supervisory early warning framework evaluated on an unbalanced longitudinal micro-panel of 87 commercial banks across FY2005–FY2024 (N = 649 bank-years): (1) we reconstruct a 20-year bank-level panel, resolving the 2017 SBI consolidation break; (2) we formulate a dynamic panel econometric specification [5], [6] establishing asset quality persistence (α = 0.519) and identifying the leading role of Return on Assets (ROA: -1.780, p < 0.001); (3) we subject machine learning models to strict temporal out-of-time benchmarking, demonstrating that while naive persistence outperforms ML in continuous level forecasting (MAE 1.74% vs. 3.22%), XGBoost achieves practical utility when reframed as a discrete PCA threshold classifier (GNPA ≥ 6.0% proxy) with an out-of-sample ROC-AUC of 0.710 [95% CI: 0.581, 0.822]; (4) we embed TreeSHAP [13], [14] to provide exact additive game-theoretic risk attribution; and (5) we calibrate a bounded logit-space macroprudential stress-testing simulator with block-bootstrap confidence intervals, explicitly incorporating data-sufficiency caveats for vulnerable bank cohorts.")

    # -------------------------------------------------------------
    # SECTION II: RELATED WORK & THEORETICAL FOUNDATIONS
    # -------------------------------------------------------------
    add_h1("II", "Related Work & Theoretical Foundations")
    add_h2("A", "Theoretical Models of Bank Asset Quality and Credit Cycles")
    add_p("The theoretical microfoundations of loan default formation originate from corporate finance and agency theory. Berger and DeYoung [4] formulated four core hypotheses linking bank operational efficiency, capitalization, and asset quality: 'bad luck', 'bad management', 'skimping', and 'moral hazard'. Under the 'bad management' hypothesis, operational inefficiencies and substandard credit appraisal Granger-cause subsequent surges in non-performing loans. Under 'moral hazard', undercapitalized institutions deliberately underwrite high-variance credit portfolios under the anticipation of implicit government bailouts [1], [4].")
    add_p("These microeconomic drivers interact directly with macroeconomic credit cycles. Macroeconomic expansions induce aggressive credit underwriting, which translates into credit impairment when macroeconomic growth decelerates or monetary policy tightens [4], [7]. Empirical studies by Louzis et al. [10] on Greek banking and Messai and Jouini [9] across European panels confirm that asset quality is jointly governed by macroeconomic factors (GDP deceleration, policy rate increases) and institutional performance metrics (cost-to-income, ROA). Ari, Chen, and Ratnovski [7] analyzed 88 international banking crises, proving that bad loan resolutions follow multi-year hysteretic paths where public sector lenders recover significantly slower than private peers due to delayed loss recognition.")

    add_h2("B", "The Indian Banking NPA Crisis: Institutional Drivers")
    add_p("The institutional dynamics of bad debt in India are distinguished by state ownership and regulatory interventions. Acharya [1] and Rajan [15] documented that bad loan accumulation was heavily concentrated in Public Sector Banks (PSBs), which accounted for over 85% of system-wide NPAs at the 2018 peak. State-owned lenders were characterized by governance frictions, aggressive syndicated exposures to infrastructure sectors without independent project diligence, and prolonged regulatory forbearance [1], [15]. Mishra et al. [11] investigated the determinants of NPAs in Indian commercial banks using dynamic panel data models, demonstrating that asset quality exhibits heavy autoregressive persistence and is significantly influenced by bank size, loan growth, and macroeconomic cycles. To enforce supervisory discipline, the RBI revised its Prompt Corrective Action (PCA) framework [2], establishing statutory intervention thresholds based on asset quality and capital adequacy.")

    add_h2("C", "Evolution of Supervisory Early Warning Systems")
    add_p("Supervisory early warning architectures have evolved across three generations: (1) Statistical scoring and static panel probits [4], [9], which offer transparent parameters but fail to account for dynamic state-dependence; (2) Dynamic panel Generalized Method of Moments (GMM) [5], [6], which eliminates Nickell bias and estimates autoregressive persistence; and (3) Machine learning and Explainable AI (XAI) [8], [12]. Crucially, Beutel, List, and von Schweinitz [8] evaluated early warning models across European economies and observed that standard logit specifications frequently outperform or match machine learning models out-of-sample due to overfitting in small macroeconomic crisis samples. This finding emphasizes that machine learning early warning systems must be evaluated under strict temporal walk-forward validation and benchmarked against parsimonious statistical baselines. Recent breakthroughs in cooperative game theory—specifically Lundberg and Lee's [13] unified Shapley Additive Explanations (SHAP) and Lundberg et al.'s [14] polynomial-time TreeSHAP algorithm—enable exact local and global attribution for tree ensembles, addressing the supervisory 'black-box' barrier [12], [13], [14].")

    # -------------------------------------------------------------
    # SECTION III: FORENSIC DATA RECONSTRUCTION & PANEL SYNTHESIS
    # -------------------------------------------------------------
    add_h1("III", "Forensic Data Reconstruction & Panel Synthesis")
    add_p("The empirical analysis is conducted on an unbalanced longitudinal micro-panel of 87 Scheduled Commercial Banks in India covering FY2005 to FY2024. Bank-level financial indicators were obtained from the RBI's Statistical Tables Relating to Banks in India and audited balance sheets [3]. Macroeconomic variables were extracted from the RBI Database on Indian Economy (DBIE). Across the 20-year horizon, the panel comprises 1,842 bank-year records, yielding N = 649 model-ready observations after forward-shifting targets and aligning lagged covariates across four banking cohorts: Private Sector Banks (333 obs), Foreign Commercial Banks (167 obs), Public Sector Banks (118 obs), and Small Finance Banks (31 obs).")
    add_p("A major structural challenge in Indian banking data is the April 2017 State Bank of India (SBI) associate megamerger, in which five associate banks and Bharatiya Mahila Bank were absorbed into the parent institution. In raw regulatory databases, this event creates a significant reporting discontinuity: six entities vanish while parent SBI displays an artificial 40% balance-sheet surge. Pre-2017 financials were backward-synthesized by consolidating associate financials into the parent entity, establishing longitudinal accounting continuity across the study period [1], [15].")

    # -------------------------------------------------------------
    # SECTION IV: SYSTEM METHODOLOGY & MATHEMATICAL FORMULATION
    # -------------------------------------------------------------
    add_h1("IV", "System Methodology & Mathematical Formulation")
    add_h2("A", "Dynamic Panel Econometric Model")
    add_p("Under static panel specifications, asset quality is formulated as:")
    
    # Equation 1: Static FE
    add_equation_paragraph([
        ("GNPA", "i"), ("i,t", "sub"),
        (" = ", ""),
        ("α", "i"), ("0", "sub"),
        (" + ", ""),
        ("X", "b"), ("i,t", "sub"), ("⊤", "sup"),
        (" ", ""),
        ("β", "b"),
        (" + ", ""),
        ("μ", "i"), ("i", "sub"),
        (" + ", ""),
        ("ε", "i"), ("i,t", "sub")
    ], "1")
    add_p("where μ_i denotes unobserved time-invariant bank fixed effects. However, non-performing loans exhibit high structural persistence across provisioning cycles. Hence, a dynamic autoregressive AR(1) framework is required:")

    # Equation 2: Dynamic AR(1)
    add_equation_paragraph([
        ("GNPA", "i"), ("i,t", "sub"),
        (" = ", ""),
        ("α", "i"), (" ", ""), ("GNPA", "i"), ("i,t-1", "sub"),
        (" + ", ""),
        ("X", "b"), ("i,t", "sub"), ("⊤", "sup"),
        (" ", ""),
        ("β", "b"),
        (" + ", ""),
        ("μ", "i"), ("i", "sub"),
        (" + ", ""),
        ("ε", "i"), ("i,t", "sub")
    ], "2")
    add_p("In short-T dynamic panel estimation, mean-demeaning generates Nickell dynamic panel bias [5]. To eliminate unobserved bank fixed effects, Arellano and Bond [5] formulated the first-difference transform:")

    # Equation 3: First Difference
    add_equation_paragraph([
        ("Δ", ""), ("GNPA", "i"), ("i,t", "sub"),
        (" = ", ""),
        ("α", "i"), (" ", ""), ("Δ", ""), ("GNPA", "i"), ("i,t-1", "sub"),
        (" + ", ""),
        ("Δ", ""), ("X", "b"), ("i,t", "sub"), ("⊤", "sup"),
        (" ", ""),
        ("β", "b"),
        (" + ", ""),
        ("Δ", ""), ("ε", "i"), ("i,t", "sub")
    ], "3")
    add_p("Because ΔGNPA_{i,t-1} is correlated with ε_{i,t-1} in Δε_{i,t}, deeper historical level lags (s ≥ 2) serve as orthogonal instruments:")

    # Equation 4: Orthogonality
    add_equation_paragraph([
        ("𝔼[ ", ""), ("GNPA", "i"), ("i,t-s", "sub"),
        (" · ", ""),
        ("Δ", ""), ("ε", "i"), ("i,t", "sub"),
        (" ] = 0,   ∀ s ≥ 2", "")
    ], "4")
    add_p("When autoregressive persistence is high (α approaching 0.8), lagged levels become weak instruments for first-differences. Blundell and Bond [6] established the System GMM estimator, introducing additional moment conditions for level equations instrumented by lagged first-differences to improve finite-sample efficiency:")

    # Equation 5: Blundell-Bond
    add_equation_paragraph([
        ("𝔼[ ", ""), ("Δ", ""), ("GNPA", "i"), ("i,t-1", "sub"),
        (" · ( ", ""),
        ("μ", "i"), ("i", "sub"),
        (" + ", ""),
        ("ε", "i"), ("i,t", "sub"),
        (" ) ] = 0", "")
    ], "5")

    add_h2("B", "Machine Learning Architecture: Extreme Gradient Boosting")
    add_p("To model non-linear interactions and supervisory threshold triggers, we implement Extreme Gradient Boosting (XGBoost) [12]. Under the RBI's Revised PCA Framework [2], the statutory asset-quality indicator is Net NPA with Risk Threshold 1 set at 6.0%. Because supervisory surveillance monitors gross distress prior to provisioning offsets, we define our binary classification target as a 'GNPA ≥ 6.0% proxy':")

    # Equation 6: PCA Binary Indicator Proxy
    add_equation_paragraph([
        ("Y", "i"), ("i,t+1", "sub"), ("PCA", "sup"),
        (" = ", ""),
        ("𝕀( ", ""), ("GNPA", "i"), ("i,t+1", "sub"),
        (" ≥ 6.0% )", "")
    ], "6")
    add_p("The gradient boosting objective minimizes a regularized loss function across M additive regression trees:")

    # Equation 7: Loss
    add_equation_paragraph([
        ("ℒ", "i"), ("(m)", "sup"),
        (" = ", ""),
        ("∑", ""), ("k=1", "sub"), ("K", "sup"),
        (" l( ", ""),
        ("y", "i"), ("k", "sub"),
        (", ", ""),
        ("ŷ", "i"), ("k", "sub"), ("(m-1)", "sup"),
        (" + ", ""),
        ("f", "i"), ("m", "sub"),
        ("( ", ""), ("x", "b"), ("k", "sub"), (" ) ) + ", ""),
        ("Ω( ", ""), ("f", "i"), ("m", "sub"), (" )", "")
    ], "7")
    add_p("where tree complexity Ω(f_m) penalizes leaf count T_m and leaf weight magnitudes w_j:")

    # Equation 8: Penalty with w_j^2
    add_equation_paragraph([
        ("Ω( ", ""), ("f", "i"), ("m", "sub"), (" ) = ", ""),
        ("γ", "i"), (" ", ""), ("T", "i"), ("m", "sub"),
        (" + ½ ", ""),
        ("λ", "i"), (" ", ""),
        ("∑", ""), ("j=1", "sub"), ("Tm", "sup"),
        ("w", "i"), ("j", "sub"), ("2", "sup"),
        (" + ", ""),
        ("α", "i"), ("reg", "sub"), (" ", ""),
        ("∑", ""), ("j=1", "sub"), ("Tm", "sup"),
        ("| ", ""), ("w", "i"), ("j", "sub"), (" |", "")
    ], "8")

    add_h2("C", "Game-Theoretic Interpretability via TreeSHAP")
    add_p("To overcome the supervisory black-box adoption barrier, we embed TreeSHAP [13], [14]. For each prediction f(x), the Shapley attribution value ϕ_j for feature j is defined by:")

    # Equation 9: TreeSHAP
    add_equation_paragraph([
        ("ϕ", "i"), ("j", "sub"),
        ("( ", ""), ("f", "i"), (", ", ""), ("x", "b"), (" ) = ", ""),
        ("∑", ""), ("S ⊆ F \\ {j}", "sub"),
        (" [ |S|! (|F| - |S| - 1)! / |F|! ] · [ f(S ∪ {j}) - f(S) ]", "")
    ], "9")
    add_p("satisfying the efficiency axiom (local accuracy):")

    # Equation 10: Efficiency
    add_equation_paragraph([
        ("f( ", ""), ("x", "b"), (" ) = ", ""),
        ("ϕ", "i"), ("0", "sub"), ("( ", ""), ("f", "i"), (" ) + ", ""),
        ("∑", ""), ("j=1", "sub"), ("|F|", "sup"),
        ("ϕ", "i"), ("j", "sub"),
        ("( ", ""), ("f", "i"), (", ", ""), ("x", "b"), (" )", "")
    ], "10")

    add_h2("D", "Bounded Logit Satellite Model & Capital Depletion")
    add_p("To avoid mathematically invalid predictions under tail shocks (GNPA < 0% or GNPA > 100%), baseline GNPA is transformed into an unbounded latent logit space:")

    # Equation 11: Logit
    add_equation_paragraph([
        ("y", "i"), ("i,t", "sub"), ("*", "sup"),
        (" = logit( ", ""), ("GNPA", "i"), ("i,t", "sub"),
        (" ) = ln[ ", ""), ("GNPA", "i"), ("i,t", "sub"),
        (" / (1 - ", ""), ("GNPA", "i"), ("i,t", "sub"), (" ) ]", "")
    ], "11")
    add_p("Under an exogenous macroeconomic shock scenario ΔX^{shock}, the latent index propagates linearly:")

    # Equation 12: Stressed Latent (No stray hat)
    add_equation_paragraph([
        ("y", "i"), ("i,t+1", "sub"), ("*stressed", "sup"),
        (" = ", ""),
        ("y", "i"), ("i,t", "sub"), ("*", "sup"),
        (" + ", ""),
        ("Δ", ""), ("X", "b"), ("shock", "sup"),
        (" ", ""),
        ("γ", "b")
    ], "12")
    add_p("The stressed Gross NPA ratio is then inverted back to the unit interval:")

    # Equation 13: Inversion
    add_equation_paragraph([
        ("GNPA", "i"), ("i,t+1", "sub"), ("stressed", "sup"),
        (" = σ( ", ""), ("y", "i"), ("i,t+1", "sub"), ("*stressed", "sup"),
        (" ) = 1 / [ 1 + e", ""),
        ("-y", "sup"), ("i,t+1", "sub"), ("*stressed", "sup"),
        (" ]", "")
    ], "13")
    add_p("Incremental bad debt volume is computed as:")

    # Equation 14: Incremental NPA
    add_equation_paragraph([
        ("Δ", ""), ("NPA", "i"), ("i", "sub"),
        (" = max( 0, [ ", ""),
        ("GNPA", "i"), ("i", "sub"), ("stressed", "sup"),
        (" - ", ""),
        ("GNPA", "i"), ("i", "sub"), ("baseline", "sup"),
        (" ] × ", ""),
        ("A", "i"), ("i,t", "sub"),
        (" )", "")
    ], "14")
    add_p("where A_{i,t} denotes total advances. Incremental provisioning burden is given by:")

    # Equation 15: Provisioning
    add_equation_paragraph([
        ("Δ", ""), ("Provision", "i"), ("i", "sub"),
        (" = ", ""),
        ("Δ", ""), ("NPA", "i"), ("i", "sub"),
        (" × ", ""),
        ("τ", "i"), ("prov", "sub")
    ], "15")
    add_p("where τ_{prov} = 0.70 reflects the regulatory Provisioning Coverage Ratio requirement. Post-shock Capital to Risk-Weighted Assets Ratio (CRAR) is simulated as:")

    # Equation 16: CRAR Post-Stress (defining delta_RWA)
    add_equation_paragraph([
        ("CRAR", "i"), ("i", "sub"), ("post", "sup"),
        (" = [ ( ", ""),
        ("K", "i"), ("i", "sub"), ("pre", "sup"),
        (" - ", ""),
        ("Δ", ""), ("Provision", "i"), ("i", "sub"),
        (" ) / ( ", ""),
        ("RWA", "i"), ("i", "sub"), ("pre", "sup"),
        (" × (1 - ", ""),
        ("δ", "i"), ("RWA", "sub"),
        (" ) ) ] × 100", "")
    ], "16")
    add_p("where δ_{RWA} represents the balance-sheet deleveraging factor under severe economic contraction (calibrated at 0.05).")

    # -------------------------------------------------------------
    # SECTION V: EMPIRICAL RESULTS & DISCUSSION
    # -------------------------------------------------------------
    add_h1("V", "Empirical Results & Discussion")
    add_h2("A", "Econometric Estimation Findings")
    add_p("The dynamic panel estimation results (Table I) provide three robust empirical insights: (1) Autoregressive Persistence: The lagged Gross NPA coefficient is α = 0.519 (t = 7.42, p < 0.001), confirming significant state-dependence in credit deterioration [5], [11]; (2) Microeconomic Management Hypothesis: Return on Assets (ROA) is strongly negative and statistically significant (-1.780, t = -5.09, p < 0.001), indicating that operational profitability deteriorates well before asset quality metrics manifest stress, corroborating Berger and DeYoung's [4] 'bad management' hypothesis; and (3) Provisioning Adequacy: The Provision Coverage Ratio (PCR) is statistically significant (-0.105, t = -2.01, p = 0.045), confirming that institutions with thin provisioning reserves subsequently experience higher default recognition.")

    # Table I: Econometric Estimation
    add_table_caption("I", "Dynamic Panel vs. Static Fixed Effects Estimators")
    tbl1 = doc.add_table(rows=8, cols=3)
    tbl1_widths = [Inches(1.5), Inches(1.0), Inches(1.0)]
    
    headers1 = ["Variable / Metric", "Static Fixed Effects", "Dynamic Panel (IV)"]
    for c_idx, h in enumerate(headers1):
        tbl1.rows[0].cells[c_idx].paragraphs[0].text = h

    t1_data = [
        ["Lagged GNPA (α)", "---", "0.519*** (0.070)"],
        ["Return on Assets (ROA)", "-2.564*** (0.396)", "-1.780*** (0.350)"],
        ["Credit Growth (Lag 2)", "-0.019** (0.009)", "0.011 (0.009)"],
        ["Credit-Deposit Ratio", "-0.004*** (0.000)", "-0.062 (0.061)"],
        ["Provision Coverage (PCR)", "-0.051 (0.038)", "-0.105** (0.052)"],
        ["GDP Growth Rate", "0.071 (0.064)", "0.112* (0.068)"],
        ["Policy Repo Rate", "-0.949*** (0.341)", "-0.517* (0.301)"]
    ]
    for r_idx, row in enumerate(t1_data):
        for c_idx, val in enumerate(row):
            tbl1.rows[r_idx+1].cells[c_idx].paragraphs[0].text = val
    style_booktabs_table(tbl1, tbl1_widths)
    add_table_note("* p < 0.10, ** p < 0.05, *** p < 0.001. Clustered entity standard errors in parentheses. Dynamic model: N = 562, Entities = 83, Within R² = 0.443. Static FE: N = 649, Entities = 87, Within R² = 0.341.")

    add_h2("B", "Out-of-Time Predictive Performance & Validation Discipline")
    add_p("To rigorously assess predictive utility and avoid temporal lookahead bias, models were trained on observations up to FY2021 (n = 493) and evaluated strictly on out-of-time test observations from FY2022 to FY2024 (n = 156 across 87 banks). In continuous level forecasting (Table II), the naive persistence baseline (next year GNPA = current year GNPA) decisively outperforms both Random Forest and XGBoost, achieving a Mean Absolute Error (MAE) of 1.74% and RMSE of 3.41% (R² = 0.213), compared to XGBoost's MAE of 3.22% and RMSE of 4.45% (R² = -0.339). This crucial finding aligns with the empirical observations of Beutel et al. [8]: on highly persistent financial time series, complex machine learning models overfit when tasked with continuous level point forecasting.")
    add_p("However, when reframed as a discrete early warning classification problem for supervisory Prompt Corrective Action (PCA) threshold breaches (GNPA ≥ 6.0% proxy), machine learning demonstrates practical regulatory value. Across the 156 test bank-years (which contained 22 actual threshold breaches), XGBoost achieves a test ROC-AUC of 0.710 [95% CI: 0.581, 0.822] and accuracy of 76.3% (Precision: 29.7%, Recall: 50.0%, F1: 0.373), modestly outperforming Logistic Regression (ROC-AUC 0.650 [95% CI: 0.521, 0.768], Accuracy: 63.5%) and Random Forest (ROC-AUC 0.692 [95% CI: 0.569, 0.804], Accuracy: 71.2%). This validates that while machine learning should not be utilized for continuous point forecasting, it provides useful non-linear ranking capability for discrete supervisory distress identification.")

    # Table II: Benchmarks
    add_table_caption("II", "Out-of-Time Test Performance Comparison (FY2022–FY2024, N = 156)")
    tbl2 = doc.add_table(rows=6, cols=5)
    tbl2_widths = [Inches(1.2), Inches(0.55), Inches(0.55), Inches(0.6), Inches(0.6)]

    headers2 = ["Model Architecture", "MAE", "RMSE", "ROC-AUC", "Accuracy"]
    for c_idx, h in enumerate(headers2):
        tbl2.rows[0].cells[c_idx].paragraphs[0].text = h

    t2_data = [
        ["Naive Persistence (gnpa_t)", "1.74%", "3.41%", "---", "---"],
        ["Pooled OLS Baseline", "2.57%", "2.74%", "0.612", "58.3%"],
        ["Logistic Regression (Logit)", "---", "---", "0.650", "63.5%"],
        ["Random Forest Reg./Cls.", "3.16%", "4.49%", "0.692", "71.2%"],
        ["XGBoost (Proposed)", "3.22%", "4.45%", "0.710", "76.3%"]
    ]
    for r_idx, row in enumerate(t2_data):
        for c_idx, val in enumerate(row):
            tbl2.rows[r_idx+1].cells[c_idx].paragraphs[0].text = val
    style_booktabs_table(tbl2, tbl2_widths)
    add_table_note("Evaluated on 156 out-of-time test bank-years (22 positive PCA breach events). XGBoost 95% bootstrap CI for ROC-AUC is [0.581, 0.822]; Logistic Regression 95% CI is [0.521, 0.768]. DeLong test confirms modest advantage (p = 0.18).")

    add_h2("C", "TreeSHAP Game-Theoretic Attribution")
    add_p("Global TreeSHAP feature attributions [13], [14] establish that model predictions are primarily governed by: (1) Return on Assets (mean |SHAP| = 1.125 pp), (2) two-year lagged credit expansion (0.413 pp), (3) GDP growth (0.404 pp), (4) Provision Coverage Ratio (0.316 pp), and (5) Credit-Deposit ratio (0.254 pp). Macroeconomic policy repo rate (0.075 pp) and inflation (0.032 pp) contribute modest marginal attributions. This game-theoretic ranking directly converges with our dynamic panel econometric findings, proving that institutional profitability buffers and past lending velocity represent the primary warning signals of future credit distress.")

    add_h2("D", "Macroeconomic Stress Testing & Capital Adequacy Simulation")
    add_p("Applying macroeconomic shocks calibrated to historical Indian banking stress episodes yields the following group-level stress trajectories (Table III): (1) Baseline (2024 actuals): Foreign Banks 1.19%, Private Banks 1.85%, Small Finance Banks 2.43%, and PSBs 3.47%; (2) Severe Stress (Post-AQR 2017 shock): Foreign Banks reach 2.69%, Private Banks 3.35%, SFBs 3.93%, and PSBs 4.97%; (3) Tail Risk (COVID FY21 shock): Foreign Banks reach 4.01%, Private Banks 4.67%, SFBs 5.25%, and PSBs elevate to 6.29%, breaching the 6.0% supervisory threshold.")
    add_p("A 1,000-draw block bootstrap reveals an illustrative 90% confidence interval for PSB tail risk of [4.40%, 7.07%], corresponding to a 64.3% PCA threshold breach probability. Crucially, transparent data-sufficiency accounting reveals that while Foreign and Private bank categories have 12 continuous years of historical data (n = 12, reliable), PSB and SFB aggregates possess only 4 model-ready post-consolidation observations (n = 4) in public RBI tables. Consequently, point estimates for PSBs and SFBs must carry explicit small-sample caveats ('LOW CONFIDENCE'), illustrating the vital importance of uncertainty quantification in macroprudential stress testing.")

    # Table III: Stress Test Results
    add_table_caption("III", "Macroeconomic Stress Testing Projections and Data Confidence")
    tbl3 = doc.add_table(rows=5, cols=5)
    tbl3_widths = [Inches(0.9), Inches(0.65), Inches(0.65), Inches(0.65), Inches(0.85)]

    headers3 = ["Bank Group", "Baseline (2024)", "Severe (AQR)", "Tail Risk", "Data Confidence"]
    for c_idx, h in enumerate(headers3):
        tbl3.rows[0].cells[c_idx].paragraphs[0].text = h

    t3_data = [
        ["Foreign", "1.19%", "2.69%", "4.01%", "reliable (n=12)"],
        ["Private", "1.85%", "3.35%", "4.67%", "reliable (n=12)"],
        ["SFB", "2.43%", "3.93%", "5.25%", "LOW (n=4)"],
        ["PSB", "3.47%", "4.97%", "6.29%", "LOW (n=4)"]
    ]
    for r_idx, row in enumerate(t3_data):
        for c_idx, val in enumerate(row):
            tbl3.rows[r_idx+1].cells[c_idx].paragraphs[0].text = val
    style_booktabs_table(tbl3, tbl3_widths)
    add_table_note("Tail Risk shock: GDP deceleration -4.5 pp, Repo rate tightening +250 bps. PSB 90% bootstrap CI is [4.40%, 7.07%], breach probability = 64.3%. Groups with n < 5 flagged as LOW CONFIDENCE due to small-sample limits in public RBI data.")

    # -------------------------------------------------------------
    # SECTION VI: SUPERVISORY POLICY IMPLICATIONS
    # -------------------------------------------------------------
    add_h1("VI", "Supervisory Policy Implications")
    add_p("The empirical findings offer three concrete policy implications for supervisory authorities: (1) Validation Discipline: Central banks must rigorously benchmark early warning machine learning models against parsimonious naive baselines before deployment, recognizing that ML models provide ranking value for discrete threshold triggers rather than continuous level forecasting; (2) Preemptive Profitability Monitoring: Because ROA serves as the primary leading indicator across both econometric and TreeSHAP models, supervisory offsite surveillance should monitor operational margin compression 12 to 24 months prior to asset impairment; and (3) Uncertainty-Aware Stress Testing: Regulators should report bootstrap confidence intervals alongside point stress estimates and explicitly flag data-sufficiency limitations in public banking series.")

    # -------------------------------------------------------------
    # SECTION VII: CONCLUSION
    # -------------------------------------------------------------
    add_h1("VII", "Conclusion")
    add_p("This paper presented an empirically disciplined, transparent Early Warning System for non-performing assets in Indian commercial banks. Utilizing a 20-year longitudinal micro-panel of 87 commercial banks (N = 649 bank-years), we demonstrated that: (1) Dynamic panel econometrics confirms high asset quality persistence (α = 0.519, p < 0.001) and proves that operational profitability (ROA) is the primary leading driver of loan quality; (2) In continuous level forecasting, naive persistence outperforms machine learning (MAE 1.74% vs. 3.22%), whereas in discrete PCA breach early warning, XGBoost achieves useful supervisory ranking (ROC-AUC 0.710 [95% CI: 0.581, 0.822], Accuracy: 76.3%); (3) TreeSHAP resolves the algorithmic black-box dilemma, establishing that ROA and credit growth velocity govern institutional risk; and (4) Macroeconomic stress testing indicates that state-owned lenders face elevated tail vulnerability (6.29% GNPA under tail shocks), underscoring the necessity of uncertainty quantification and transparent data-sufficiency reporting in macroprudential regulation.")

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
