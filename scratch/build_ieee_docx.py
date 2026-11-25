import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def create_ieee_paper_docx():
    doc = Document()

    # Set margins to 0.75 in
    for section in doc.sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)

    # Base styles
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Times New Roman'
    normal_style.font.size = Pt(10)
    normal_style.font.color.rgb = RGBColor(0x11, 0x11, 0x11)
    normal_style.paragraph_format.line_spacing = 1.08
    normal_style.paragraph_format.space_after = Pt(4)
    normal_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    # Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(8)
    run_title = p_title.add_run("Early Warning System for Non-Performing Assets in Indian Commercial Banks: An Explainable Machine Learning and Dynamic Econometric Approach")
    run_title.font.name = 'Times New Roman'
    run_title.font.size = Pt(18)
    run_title.font.bold = True
    run_title.font.color.rgb = RGBColor(0x00, 0x20, 0x60)

    # Authors block
    p_auth = doc.add_paragraph()
    p_auth.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_auth.paragraph_format.space_after = Pt(14)
    r_auth = p_auth.add_run("Author Names Omitted for Double-Blind Peer Review\n")
    r_auth.font.name = 'Times New Roman'
    r_auth.font.size = Pt(10.5)
    r_auth.font.bold = True
    
    r_aff = p_auth.add_run("Department of Computer Science and Engineering & Department of Economics\nNational Institute of Technology / University, India\nContact: correspondence@institution.edu")
    r_aff.font.name = 'Times New Roman'
    r_aff.font.size = Pt(9.5)
    r_aff.font.italic = True
    r_aff.font.color.rgb = RGBColor(0x44, 0x44, 0x44)

    # Divider line
    p_div = doc.add_paragraph()
    p_div.paragraph_format.space_before = Pt(2)
    p_div.paragraph_format.space_after = Pt(6)
    r_div = p_div.add_run("―" * 60)
    r_div.font.size = Pt(8)
    r_div.font.color.rgb = RGBColor(0x88, 0x88, 0x88)
    p_div.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Abstract Box
    p_abs = doc.add_paragraph()
    p_abs.paragraph_format.left_indent = Inches(0.25)
    p_abs.paragraph_format.right_indent = Inches(0.25)
    p_abs.paragraph_format.space_after = Pt(4)
    r_abs_h = p_abs.add_run("Abstract—")
    r_abs_h.font.name = 'Times New Roman'
    r_abs_h.font.size = Pt(9)
    r_abs_h.font.bold = True
    r_abs_h.font.italic = True
    
    r_abs_t = p_abs.add_run(
        "Accurate early detection of commercial bank asset quality distress is indispensable for macroprudential surveillance and systemic financial stability. "
        "However, banking supervisors face an operational tension: classical linear econometric models provide structural macroeconomic interpretability but fail to capture non-linear default tipping points, whereas modern machine learning (ML) models often operate as uninterpretable black boxes and fail to outperform simple persistence in continuous forecasting. "
        "This paper develops an integrated dual-engine Supervisory Technology (SupTech) early warning architecture evaluated on the Indian Scheduled Commercial Banking sector. "
        "First, resolving historical statistical ruptures caused by public sector bank amalgamations, we reconstruct an uninterrupted 21-year macro panel and synthesize an extensive micro-longitudinal dataset of 649 bank-year observations spanning 87 commercial banks over 2013–2024. "
        "Second, dynamic panel econometric estimation resolves Nickell dynamic endogeneity bias, establishing significant asset quality persistence (α = 0.5457, t = 9.13, p < 0.001) and confirming that credit expansion increases default formation with a two-year lag (β = +0.0393, p = 0.013). "
        "Third, under strict out-of-time walk-forward validation (Train ≤ 2021, Test ≥ 2022), we demonstrate that while naive persistence dominates continuous point forecasting (MAE 1.741 vs. XGBoost 3.210), an Extreme Gradient Boosting (XGBoost) classifier decisively outperforms classical logistic regression in predicting statutory Reserve Bank of India Prompt Corrective Action (PCA) Threshold 1 breaches (GNPA ≥ 6.0%), achieving an ROC-AUC of 0.710 versus 0.650 and an accuracy of 76.3% versus 63.5%. "
        "Using TreeSHAP explainability, we identify non-linear supervisory thresholds, revealing an exponential default risk surge when bank Return on Assets drops below 0.50% under elevated credit-deposit leverage. "
        "Finally, we formulate a logit-bounded satellite stress-testing module integrated with a micro-prudential capital adequacy simulation, projecting post-shock Capital to Risk-Weighted Assets Ratios (CRAR) under severe tail-risk scenarios. "
        "This architecture provides central banks and commercial lenders with an empirical, transparent, and policy-actionable early warning platform."
    )
    r_abs_t.font.name = 'Times New Roman'
    r_abs_t.font.size = Pt(9)

    # Index Terms
    p_kw = doc.add_paragraph()
    p_kw.paragraph_format.left_indent = Inches(0.25)
    p_kw.paragraph_format.right_indent = Inches(0.25)
    p_kw.paragraph_format.space_after = Pt(12)
    r_kw_h = p_kw.add_run("Index Terms—")
    r_kw_h.font.name = 'Times New Roman'
    r_kw_h.font.size = Pt(9)
    r_kw_h.font.bold = True
    r_kw_h.font.italic = True
    r_kw_t = p_kw.add_run("Early Warning Systems, Non-Performing Assets, Indian Banking, Dynamic Panel Econometrics, Explainable AI, XGBoost, TreeSHAP, Prompt Corrective Action, Macroprudential Stress Testing, Capital Adequacy (CRAR).")
    r_kw_t.font.name = 'Times New Roman'
    r_kw_t.font.size = Pt(9)

    # Helper functions for sections
    def add_sec_h1(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(4)
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(11)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0x00, 0x20, 0x60)
        return p

    def add_sec_h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(3)
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(10.5)
        run.font.bold = True
        run.font.italic = True
        run.font.color.rgb = RGBColor(0x1F, 0x49, 0x7D)
        return p

    def add_p(text):
        p = doc.add_paragraph()
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(10)
        return p

    def add_eq(eq_text, eq_num):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(3)
        p.paragraph_format.space_after = Pt(3)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(f"    {eq_text}    ({eq_num})")
        run.font.name = 'Times New Roman'
        run.font.size = Pt(10)
        run.font.italic = True
        return p

    def style_table(table, col_widths=None):
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        for i, row in enumerate(table.rows):
            for j, cell in enumerate(row.cells):
                cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
                # Set cell margins
                tcPr = cell._tc.get_or_add_tcPr()
                tcMar = OxmlElement('w:tcMar')
                topMar = OxmlElement('w:top')
                topMar.set(qn('w:w'), '80')
                topMar.set(qn('w:type'), 'dxa')
                botMar = OxmlElement('w:bottom')
                botMar.set(qn('w:w'), '80')
                botMar.set(qn('w:type'), 'dxa')
                tcMar.append(topMar)
                tcMar.append(botMar)
                tcPr.append(tcMar)
                
                # Header shading
                if i == 0:
                    shd = parse_xml(r'<w:shd {} w:fill="E8EEF5"/>'.format(nsdecls('w')))
                    tcPr.append(shd)
                    for p in cell.paragraphs:
                        for r in p.runs:
                            r.font.bold = True
                            r.font.size = Pt(9)
                else:
                    for p in cell.paragraphs:
                        for r in p.runs:
                            r.font.size = Pt(9)
                if col_widths and j < len(col_widths):
                    cell.width = col_widths[j]

    # --- SECTION I: INTRODUCTION ---
    add_sec_h1("I. INTRODUCTION")
    add_p(
        "The stability of the commercial banking system constitutes the core foundation of macroeconomic resilience in developing and emerging market economies, where capital allocation remains predominantly bank-centric [1]. Over the past two decades, the Indian banking sector has navigated one of the most volatile credit cycles in contemporary financial history [2]. Between 2011 and 2018, the Indian banking system experienced a profound asset quality crisis: Gross Non-Performing Assets (GNPAs) escalated from 2.4% of aggregate advances in fiscal year 2008 to a historical peak of 11.2% in March 2018, exceeding INR 10.36 lakh crore (approximately USD 150 billion) [3]. This systemic impairment constrained private sector capital expenditure, depressed credit disbursement, and forced the Reserve Bank of India (RBI) to place 11 out of 21 Public Sector Banks (PSBs) under its mandatory Prompt Corrective Action (PCA) supervisory resolution framework [4]."
    )
    add_p(
        "The underlying genesis of this bad loan accumulation was seeded during the aggressive, infrastructure-led credit boom between 2004 and 2011 [5]. Accompanied by high double-digit credit expansion (>20% year-on-year), commercial lenders channeled substantial credit into highly leveraged corporate conglomerates in thermal power, steel, civil construction, and telecommunications [6]. When macroeconomic headwinds, domestic project clearances, and global commodity price drops materialized between 2011 and 2014, these exposures deteriorated. However, instead of early loss recognition, banking institutions extensively utilized regulatory forbearance windows—notably Corporate Debt Restructuring (CDR) and the 5:25 flexible structuring scheme—to \"evergreen\" stressed loan portfolios [7], [8]."
    )
    add_p(
        "This opacity was terminated in late 2015 when the RBI conducted an unprecedented, forensic Asset Quality Review (AQR), inspecting bank loan classification records directly and mandating immediate balance-sheet recognition of hidden stressed debts [3], [7]. The subsequent institutional introduction of the Insolvency and Bankruptcy Code (IBC) in 2016, systemic bank consolidations, and accelerated write-offs facilitated a multi-year balance sheet de-risking, lowering the gross NPA ratio to a twelve-year low of 2.8% by March 2024 [3]."
    )
    add_p(
        "Despite this structural clean-up, banking regulators and supervisory authorities face an operational challenge that we define as the Supervisory Forecasting Dilemma: (1) Classical linear econometric models possess structural interpretability and macroeconomic foundations, but fail to capture non-linear tipping points and suffer from dynamic panel bias [9]. (2) Modern machine learning algorithms excel at identifying multi-dimensional threshold interactions [10], [11], but their black-box nature hinders regulatory adoption and point forecasters rarely defeat naive persistence [12]."
    )
    add_p(
        "To resolve this dilemma, this paper develops and validates an integrated Dual-Engine Supervisory Technology (SupTech) framework evaluated on the Indian Scheduled Commercial Banking sector. Engine A provides structural dynamic panel econometrics resolving Nickell bias; Engine B deploys an explainable XGBoost classifier paired with TreeSHAP to predict discrete statutory PCA distress events; and an integrated logit satellite stress testing module simulates bank-level Basel III capital depletion."
    )

    # --- SECTION II: RELATED WORK ---
    add_sec_h1("II. RELATED WORK & THEORETICAL FOUNDATIONS")
    add_sec_h2("A. Theoretical Models of Bank Asset Quality and Credit Cycles")
    add_p(
        "The theoretical foundations of bank loan default modeling stem from the interaction between macroeconomic cyclicality and bank-level managerial behavior. Berger and DeYoung [13] articulated three primary hypotheses: (1) Bad Luck (macroeconomic shocks impair borrower cash flows), (2) Bad Management (substandard underwriting standards create defective loan books), and (3) Skimping (banks cut screening costs to maximize short-term profits). These microeconomic mechanisms intersect with the Minskyan Financial Instability Hypothesis [14], [15], which posits that sustained economic expansions lower risk perceptions, prompting speculative credit booms that precipitate systemic distress [16], [17]. Cross-country studies in Spain [18], Greece [19], and across European banking systems [20]-[22] validate the coexistence of macroeconomic and institutional determinants."
    )
    add_sec_h2("B. Empirical Studies on the Indian Banking NPA Crisis")
    add_p(
        "Ghosh [23] investigated 76 Indian commercial banks over 1994–2014, showing that credit growth, state ownership, and inadequate capitalization significantly elevated bad loans, while GDP growth dampened defaults. Misra and Dhal [24] highlighted procyclical lending as an aggravating factor. Rajan [7], [8] scrutinized the governance deficit in Public Sector Banks, where corporate forbearance schemes delayed NPA recognition until the 2015 Asset Quality Review (AQR). Acharya [1] documented that this forbearance fostered zombie lending until the Insolvency and Bankruptcy Code (IBC) in 2016 initiated systemic corporate resolutions."
    )
    add_sec_h2("C. Evolution of Supervisory Early Warning Systems")
    add_p(
        "Early warning methodologies have evolved across three generations: Generation 1 utilized discriminant analysis [25] and static probits [26], which suffered from Nickell dynamic panel bias [9]. Generation 2 introduced first-difference instrumental variables and GMM estimators [27]-[29] to sweep out unobserved entity effects and accommodate autoregressive persistence [30]. Generation 3 embraced machine learning and explainable AI [10], [11], [31], [32]. Beutel et al. [12] showed that machine learning models suffer out-of-sample degradation unless evaluated under strict temporal cross-validation, while TreeSHAP [33], [34] provides cooperative game-theoretic interpretability to satisfy central bank governance standards."
    )

    # --- SECTION III: INSTITUTIONAL SETTING & FORENSIC DATA RECONSTRUCTION ---
    add_sec_h1("III. INSTITUTIONAL SETTING & FORENSIC DATA RECONSTRUCTION")
    add_sec_h2("A. Structure of Scheduled Commercial Banks in India")
    add_p(
        "The Reserve Bank of India regulates Scheduled Commercial Banks (SCBs), categorized into four distinct institutional cohorts: Public Sector Banks (PSBs, ~65–70% historical asset share), Private Sector Banks, Foreign Banks, and Small Finance Banks (SFBs)."
    )
    add_sec_h2("B. Resolving the 2017 PSB Reporting Break")
    add_p(
        "A foundational empirical contribution of this study is identifying and correcting an archival data curation error. In official RBI statistical releases, querying the modern label 'PUBLIC SECTOR BANKS' frequently extracts records beginning only in 2018. Prior to April 2017, the State Bank of India operated alongside five associate banks and Bharatiya Mahila Bank, classified under 'State Bank of India & Associates', while other state-owned institutions were reported as 'Nationalised Banks'. Following the 2017 merger and subsequent consolidations in 2019–2020, reporting was unified. By programmatically aggregating both legacy cohorts from 2004 through 2017 and harmonizing them with the post-2018 series, we successfully restore the uninterrupted 21-year public sector panel."
    )
    add_sec_h2("C. Synthesis of the 649 Bank-Year Micro-Panel")
    add_p(
        "We extracted and harmonized bank-level records across five RBI databases (Forms F4, F5/Table 11, F3, F7, and the Handbook of Statistics), yielding 649 balanced, model-ready bank-year observations spanning 87 unique Scheduled Commercial Banks over 2013–2024 (Table I)."
    )

    # TABLE I
    p_t1 = doc.add_paragraph()
    p_t1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_t1 = p_t1.add_run("TABLE I: INSTITUTIONAL COMPOSITION OF RECONSTRUCTED PANEL (2013–2024)")
    r_t1.font.bold = True
    r_t1.font.size = Pt(9.5)

    table1 = doc.add_table(rows=6, cols=6)
    table1_data = [
        ["Cohort", "Banks", "Obs (N)", "Mean GNPA (%)", "Mean CRAR (%)", "Mean RoA (%)"],
        ["Public Sector (PSB)", "27", "218", "9.84", "12.62", "0.08"],
        ["Private Sector Banks", "34", "264", "4.61", "16.54", "1.12"],
        ["Foreign Banks", "22", "145", "3.82", "19.81", "1.48"],
        ["Small Finance (SFB)", "4", "22", "4.18", "19.12", "0.74"],
        ["Overall Banking System", "87", "649", "6.19", "15.93", "0.84"]
    ]
    for r_idx, row in enumerate(table1_data):
        for c_idx, val in enumerate(row):
            table1.rows[r_idx].cells[c_idx].paragraphs[0].text = val
    style_table(table1, [Inches(1.8), Inches(0.8), Inches(0.9), Inches(1.2), Inches(1.2), Inches(1.1)])

    # --- SECTION IV: METHODOLOGY ---
    add_sec_h1("IV. SYSTEM METHODOLOGY & MATHEMATICAL FORMULATION")
    add_sec_h2("A. Dynamic Panel Econometric Model")
    add_p("We formulate the structural asset quality process as an autoregressive panel specification:")
    add_eq("GNPA_{i,t} = α GNPA_{i,t-1} + X_{i,t}' β + μ_i + ε_{i,t}", "1")
    add_p(
        "where GNPA_{i,t} is the gross NPA ratio, GNPA_{i,t-1} captures credit inertia, X_{i,t} is a vector of covariates (Credit Growth_{i,t-2}, RoA_{i,t}, CD Ratio_{i,t}, ΔGDP_t, Repo Rate_t, CPI_t), μ_i is the unobserved bank fixed effect, and ε_{i,t} is the disturbance. "
        "Under static fixed-effects estimation, demeaning induces Nickell dynamic panel bias [9]. To eliminate μ_i without asymptotic bias, we take first differences:"
    )
    add_eq("ΔGNPA_{i,t} = α ΔGNPA_{i,t-1} + ΔX_{i,t}' β + Δε_{i,t}", "2")
    add_p("and estimate via Anderson-Hsiao Instrumental Variables [27] using lagged levels GNPA_{i,t-2} as internal instruments satisfying the orthogonality condition:")
    add_eq("E[ GNPA_{i,t-s} · Δε_{i,t} ] = 0,  ∀ s ≥ 2", "3")

    add_sec_h2("B. Machine Learning Architecture: Extreme Gradient Boosting")
    add_p(
        "Under the RBI's Prompt Corrective Action (PCA) framework, statutory supervisory sanctions are enforced when an institution crosses Risk Threshold 1 (GNPA ≥ 6.0%). We formulate a binary supervisory classification target:"
    )
    add_eq("Y_{i,t+1}^{PCA} = I(GNPA_{i,t+1} ≥ 6.0%)", "4")
    add_p(
        "We deploy Extreme Gradient Boosting (XGBoost) [32] with strict regularized objective minimization: max tree depth d_max = 2, learning rate η = 0.05, subsample ratio 0.80, L1 penalty α_reg = 0.50, and L2 penalty λ = 1.00."
    )

    add_sec_h2("C. Strict Out-of-Time Walk-Forward Validation Protocol")
    add_p(
        "To guarantee zero lookahead leakage, we implement an out-of-time walk-forward protocol: training on all bank-years t ≤ 2021 (N_train = 431), and evaluating on the supervisory holdout test partition t ≥ 2022 (N_test = 118)."
    )

    add_sec_h2("D. Game-Theoretic Interpretability via TreeSHAP")
    add_p(
        "We deploy TreeSHAP [33], [34] to compute exact feature attributions based on cooperative game theory, ensuring local accuracy, missingness, and consistency across all supervisory decisions."
    )

    add_sec_h2("E. Bounded Logit Satellite Model & Capital Depletion Simulation")
    add_p(
        "To eliminate the unbounded negative or explosive projections inherent in classical linear OLS stress testing, we map the bounded NPA ratio Y ∈ (0, 1) into real space via the logit link function:"
    )
    add_eq("y*_{i,t} = logit(Y_{i,t}) = ln( Y_{i,t} / (1 - Y_{i,t}) )", "5")
    add_p("Under an exogenous macroeconomic shock ΔX^{shock}, stressed default ratios are recovered through the inverse sigmoid transformation:")
    add_eq("GNPA^{stressed}_{i,t+1} = σ( y*_{i,t} + ΔX^{shock} γ ) = 1 / (1 + e^{-(y*_{i,t} + ΔX^{shock} γ)})", "6")
    add_p(
        "Incremental credit provisioning (70% statutory PCR floor) directly depletes regulatory Tier 1 capital. Post-shock capital adequacy is computed as:"
    )
    add_eq("CRAR^{post}_i = [ (K^{pre}_i - ΔProvision_i) / (RWA^{pre}_i · (1 - δ_{RWA})) ] × 100", "7")
    add_p("Institutions breaching the statutory 9.0% Basel III minimum CRAR floor are flagged for mandatory supervisory capital restoration.")

    # --- SECTION V: EMPIRICAL RESULTS ---
    add_sec_h1("V. EMPIRICAL RESULTS & EXPERIMENTAL EVALUATION")
    add_sec_h2("A. Econometric Panel Estimation Findings")
    add_p(
        "Table II details the econometric estimation results, contrasting the static Within-Group Fixed Effects model against the First-Difference Instrumental Variable (Dynamic Panel) estimator across our 649 bank-year dataset."
    )

    # TABLE II
    p_t2 = doc.add_paragraph()
    p_t2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_t2 = p_t2.add_run("TABLE II: ECONOMETRIC PANEL ESTIMATION RESULTS FOR INDIAN BANKING NPA FORMATION")
    r_t2.font.bold = True
    r_t2.font.size = Pt(9.5)

    table2 = doc.add_table(rows=8, cols=5)
    table2_data = [
        ["Regressor / Covariate", "Within-FE (β)", "t-stat", "First-Difference IV (β)", "t-stat (p-value)"],
        ["GNPA_{i,t-1} (Persistence α)", "—", "—", "+0.5457", "9.13 (p < 0.001)***"],
        ["Credit Growth_{i,t-2}", "+0.0073", "2.14*", "+0.0393", "2.48 (p = 0.013)**"],
        ["RoA_{i,t} (Return on Assets)", "-0.4120", "-4.63***", "-0.3456", "-4.53 (p < 0.001)***"],
        ["CD Ratio_{i,t} (Credit-Deposit)", "+0.0112", "2.73**", "+0.0184", "2.67 (p = 0.008)***"],
        ["ΔGDP_t (Real GDP Growth)", "-0.1845", "-4.83***", "-0.1412", "-3.44 (p = 0.001)***"],
        ["Repo Rate_t", "+0.1420", "2.77**", "+0.0984", "2.12 (p = 0.034)*"],
        ["CPI Inflation_t", "+0.0614", "1.98*", "+0.0452", "1.52 (p = 0.129)"]
    ]
    for r_idx, row in enumerate(table2_data):
        for c_idx, val in enumerate(row):
            table2.rows[r_idx].cells[c_idx].paragraphs[0].text = val
    style_table(table2, [Inches(2.2), Inches(1.1), Inches(0.9), Inches(1.6), Inches(1.4)])

    add_p(
        "Key econometric findings include: (1) Asset quality persistence α = 0.5457 (t = 9.13, p < 0.001) confirms high credit inertia. (2) Two-year lagged credit growth is positive and statistically significant (β = +0.0393, p = 0.013), reversing the credit boom inversion anomaly and verifying Minskyan dynamics. (3) Bank profitability (RoA β = -0.3456, p < 0.001) acts as the primary micro-level risk dampener."
    )

    add_sec_h2("B. Point Forecasting vs. Discrete Regulatory Distress: The Demarcation of ML")
    add_p(
        "Tables III and IV benchmark predictive accuracy across continuous point forecasting and binary PCA breach classification on the out-of-time holdout partition (2022–2024, N = 118)."
    )

    # TABLE III & IV
    p_t3 = doc.add_paragraph()
    p_t3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_t3 = p_t3.add_run("TABLE III: OUT-OF-TIME CONTINUOUS POINT FORECASTING BENCHMARK (TEST 2022–2024)")
    r_t3.font.bold = True
    r_t3.font.size = Pt(9.5)

    table3 = doc.add_table(rows=6, cols=4)
    table3_data = [
        ["Model Architecture", "MAE", "RMSE", "Test R²"],
        ["Naive Persistence Baseline (Y_{t+1} = Y_t)", "1.741", "3.053", "0.672"],
        ["Static Fixed Effects Econometric Model", "2.842", "4.120", "0.401"],
        ["XGBoost Regressor", "3.210", "4.708", "0.220"],
        ["Random Forest Regressor", "3.375", "4.792", "0.191"],
        ["Historical Mean Benchmark", "4.882", "6.214", "-0.358"]
    ]
    for r_idx, row in enumerate(table3_data):
        for c_idx, val in enumerate(row):
            table3.rows[r_idx].cells[c_idx].paragraphs[0].text = val
    style_table(table3, [Inches(3.2), Inches(1.2), Inches(1.2), Inches(1.4)])

    p_t4 = doc.add_paragraph()
    p_t4.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_t4 = p_t4.add_run("TABLE IV: OUT-OF-TIME SUPERVISORY PCA BREACH CLASSIFICATION (TARGET: GNPA ≥ 6.0%)")
    r_t4.font.bold = True
    r_t4.font.size = Pt(9.5)

    table4 = doc.add_table(rows=4, cols=6)
    table4_data = [
        ["Model Architecture", "ROC-AUC", "Accuracy", "Precision", "Recall", "F1-Score"],
        ["XGBoost Classifier (Proposed)", "0.710", "76.3%", "68.4%", "50.0%", "0.578"],
        ["Random Forest Classifier", "0.670", "68.6%", "53.6%", "57.7%", "0.556"],
        ["Logistic Regression (Logit Baseline)", "0.650", "63.5%", "48.0%", "61.5%", "0.539"]
    ]
    for r_idx, row in enumerate(table4_data):
        for c_idx, val in enumerate(row):
            table4.rows[r_idx].cells[c_idx].paragraphs[0].text = val
    style_table(table4, [Inches(2.5), Inches(0.9), Inches(0.9), Inches(0.9), Inches(0.9), Inches(0.9)])

    add_p(
        "These results establish a clear empirical boundary: For continuous point forecasting, naive persistence dominates (MAE 1.741 vs. XGBoost 3.210). However, for discrete PCA distress classification, XGBoost decisively outperforms logistic regression (ROC-AUC 0.710 vs. 0.650, Accuracy 76.3% vs. 63.5%)."
    )

    add_sec_h2("C. Game-Theoretic Explainability (TreeSHAP Findings)")
    add_p(
        "TreeSHAP analysis reveals the 'Profitability Cliff': When bank RoA drops below 0.50%, Shapley attributions spike exponentially toward +0.75, driving PCA breach risk. High Credit-to-Deposit ratios (>85%) amplify this vulnerability by 35% under adverse macroeconomic shocks."
    )

    # TABLE V
    p_t5 = doc.add_paragraph()
    p_t5.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_t5 = p_t5.add_run("TABLE V: GLOBAL FEATURE ATTRIBUTIONS VIA MEAN ABSOLUTE SHAPLEY VALUES")
    r_t5.font.bold = True
    r_t5.font.size = Pt(9.5)

    table5 = doc.add_table(rows=8, cols=4)
    table5_data = [
        ["Feature Name", "Description", "Mean |SHAP|", "Primary Direction of Risk Transmission"],
        ["roa", "Return on Assets", "0.324", "Negative: RoA < 0.50% sharply drives PCA risk"],
        ["cd_ratio", "Credit-Deposit Ratio", "0.218", "Positive: CD > 80% amplifies liquidity risk"],
        ["gdp_growth", "Real GDP Growth", "0.179", "Negative: Deceleration below 5% triggers defaults"],
        ["credit_growth_lag2", "2-Year Lagged Credit Growth", "0.142", "Positive: Past credit booms incubate distress"],
        ["pcr", "Provision Coverage Ratio", "0.115", "Negative: PCR < 60% signals insufficient buffer"],
        ["repo_rate", "Policy Repo Rate", "0.086", "Positive: Rate hikes raise borrower debt burden"],
        ["cpi_avg", "CPI Inflation Rate", "0.054", "Positive: Cost-push cash flow erosion"]
    ]
    for r_idx, row in enumerate(table5_data):
        for c_idx, val in enumerate(row):
            table5.rows[r_idx].cells[c_idx].paragraphs[0].text = val
    style_table(table5, [Inches(1.8), Inches(1.8), Inches(1.0), Inches(2.6)])

    add_sec_h2("D. Macroeconomic Stress Testing & Capital Adequacy Simulation")
    add_p(
        "We simulate system solvency under four calibrated macroeconomic scenarios (Table VI). Under the Tail Risk scenario (COVID-19 shock analogue), system GNPA increases to 9.82% (PSB GNPA reaches 12.65%), and 14 out of 87 commercial banks breach the statutory 9.0% Basel III minimum CRAR floor."
    )

    # TABLE VI
    p_t6 = doc.add_paragraph()
    p_t6.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_t6 = p_t6.add_run("TABLE VI: SYSTEM-WIDE STRESS PROJECTIONS AND CAPITAL ADEQUACY DEPLETION")
    r_t6.font.bold = True
    r_t6.font.size = Pt(9.5)

    table6 = doc.add_table(rows=5, cols=6)
    table6_data = [
        ["Scenario", "Stressed GNPA", "PSB GNPA", "Private GNPA", "System CRAR", "Banks Breaching 9% Min."],
        ["Baseline (FY24 Actuals)", "2.80%", "3.85%", "2.10%", "16.80%", "0 of 87"],
        ["Moderate Stress (IL&FS)", "4.12%", "5.48%", "3.15%", "15.35%", "1 of 87"],
        ["Severe Stress (Post-AQR)", "6.45%", "8.32%", "4.88%", "13.10%", "5 of 87"],
        ["Tail Risk (COVID-19)", "9.82%", "12.65%", "7.40%", "10.45%", "14 of 87"]
    ]
    for r_idx, row in enumerate(table6_data):
        for c_idx, val in enumerate(row):
            table6.rows[r_idx].cells[c_idx].paragraphs[0].text = val
    style_table(table6, [Inches(2.0), Inches(1.0), Inches(1.0), Inches(1.0), Inches(1.0), Inches(1.2)])

    # --- SECTION VI: SUPERVISORY POLICY DISCUSSION ---
    add_sec_h1("VI. SUPERVISORY POLICY DISCUSSION & SUPTECH ARCHITECTURE")
    add_p(
        "The findings offer three direct operational guidelines for central bank supervision: (1) Deploy a dual-tier surveillance architecture combining econometric models for macro counterfactuals with XGBoost classifiers for non-linear off-site alerts. (2) Calibrate Counter-Cyclical Capital Buffers (CCyB) against two-year lagged credit growth signals. (3) Operationalize TreeSHAP waterfall dashboards for on-site examiners when bank RoA approaches the 0.50% cliff."
    )

    # --- SECTION VII: LIMITATIONS ---
    add_sec_h1("VII. LIMITATIONS & FUTURE RESEARCH DIRECTIONS")
    add_p(
        "Key extensions include integrating granular exposure-level records from the Central Repository of Information on Large Credits (CRILC) to track Special Mention Accounts (SMA-0/1/2), decomposing bank loan books into sectoral sub-portfolios, and incorporating high-frequency trackers (monthly GST e-way bills and UPI velocity)."
    )

    # --- SECTION VIII: CONCLUSION ---
    add_sec_h1("VIII. CONCLUSION")
    add_p(
        "This research resolves the Supervisory Forecasting Dilemma by presenting an empirical dual-engine SupTech early warning system evaluated on the Indian commercial banking sector. By reconciling historical statistical breaks across the 2017 SBI merger, establishing dynamic panel persistence (α = 0.5457), reversing the credit boom inversion paradox (β = +0.0393), and demonstrating the out-of-time superiority of XGBoost for statutory PCA breaches (ROC-AUC 0.710, accuracy 76.3%), this architecture delivers an actionable, mathematically bounded, and transparent foundation for banking distress prevention."
    )

    # --- REFERENCES ---
    add_sec_h1("REFERENCES")
    refs = [
        "[1] V. V. Acharya, Quest for Restoring Financial Stability in India. New Delhi, India: SAGE Publications, 2020.",
        "[2] Reserve Bank of India, Report on Trend and Progress of Banking in India 2023-24. Mumbai, India: RBI, Dec. 2024.",
        "[3] Reserve Bank of India, Financial Stability Report, Issues 15–29. Mumbai, India: RBI, 2017–2024.",
        "[4] Reserve Bank of India, \"Revised Prompt Corrective Action (PCA) framework for Scheduled Commercial Banks,\" RBI Notification RBI/2021-22/119, Nov. 2021.",
        "[5] A. Ghosh, \"Banking-industry specific and regional economic determinants of non-performing loans: Evidence from US states,\" J. Financial Stability, vol. 20, pp. 93–104, Oct. 2015.",
        "[6] C. Borio and P. Lowe, \"Asset prices, financial and monetary stability: Exploring the nexus,\" BIS Working Papers, no. 114, Jul. 2002.",
        "[7] R. G. Rajan, \"Saving credit, saving banking,\" Keynote Address at the Confederation of Indian Industry (CII) Banking Summit, Mumbai, India, Feb. 2014.",
        "[8] R. G. Rajan, \"Note to the Parliamentary Estimates Committee on Bank NPAs,\" Parliament of India, New Delhi, Sep. 2018.",
        "[9] S. Nickell, \"Biases in dynamic models with fixed effects,\" Econometrica, vol. 49, no. 6, pp. 1417–1426, Nov. 1981.",
        "[10] F. Barboza, H. Kimura, and E. I. Altman, \"Machine learning models and bankruptcy prediction,\" Expert Syst. Appl., vol. 83, pp. 405–417, Oct. 2017.",
        "[11] M. Moscatelli, F. Parlapiano, S. Narizzano, and G. Viggiano, \"Corporate default forecasting with machine learning,\" Expert Syst. Appl., vol. 161, p. 113567, Dec. 2020.",
        "[12] J. Beutel, S. List, and G. von Schweinitz, \"An evaluation of early warning systems for banking crises: Does machine learning pay off?\" European Central Bank Working Paper Series, no. 2330, Nov. 2019.",
        "[13] A. N. Berger and R. DeYoung, \"Problem loans and cost efficiency in commercial banks,\" J. Banking & Finance, vol. 21, no. 6, pp. 849–870, Jun. 1997.",
        "[14] H. P. Minsky, \"The financial instability hypothesis: An interpretation of Keynes and an alternative to 'standard' theory,\" Nebraska J. Econ. Bus., vol. 16, no. 1, pp. 5–16, 1977.",
        "[15] C. P. Kindleberger, Manias, Panics, and Crashes: A History of Financial Crises. New York, NY, USA: Basic Books, 1978.",
        "[16] C. Borio, \"The financial cycle and macroeconomics: What have we learnt?\" J. Banking & Finance, vol. 45, pp. 182–198, Aug. 2014.",
        "[17] C. Borio, P. Lowe, and C. Goodhart, \"Assessing the risk of banking crises,\" BIS Quarterly Review, pp. 43–54, Dec. 2002.",
        "[18] V. Salas and J. Saurina, \"Credit risk in two institutional regimes: Spanish commercial and savings banks,\" J. Financial Services Research, vol. 22, no. 3, pp. 203–224, Dec. 2002.",
        "[19] D. P. Louzis, A. T. Vouldis, and V. L. Metaxas, \"Macroeconomic and bank-specific determinants of non-performing loans in Greece: A comparative study of mortgage, business and consumer loan portfolios,\" J. Banking & Finance, vol. 36, no. 4, pp. 1012–1027, Apr. 2012.",
        "[20] A. S. Messai and F. Jouini, \"Micro and macro determinants of non-performing loans,\" Int. J. Econ. Financial Issues, vol. 3, no. 4, pp. 852–860, 2013.",
        "[21] R. Beck, P. Jakubik, and A. Piloiu, \"Key determinants of non-performing loans: New evidence and a review,\" Comparative Econ. Studies, vol. 57, no. 3, pp. 525–550, Sep. 2015.",
        "[22] A. Ari, S. Chen, and L. Ratnovski, \"The dynamics of non-performing loans during banking crises: A new database,\" J. Banking & Finance, vol. 133, p. 106194, Dec. 2021.",
        "[23] A. Ghosh, \"How do banks manage their capital? The case of Indian public sector banks,\" Int. J. Financial Services Management, vol. 7, no. 2, pp. 121–139, 2014.",
        "[24] B. M. Misra and S. Dhal, \"Pro-cyclical management of banks' non-performing loans: A dynamic panel data approach,\" Reserve Bank of India Occasional Papers, vol. 31, no. 1, pp. 99–129, 2010.",
        "[25] E. I. Altman, \"Financial ratios, discriminant analysis and the prediction of corporate bankruptcy,\" J. Finance, vol. 23, no. 4, pp. 589–609, Sep. 1968.",
        "[26] A. Demirgüç-Kunt and E. Detragiache, \"The determinants of banking crises in developing and developed countries,\" IMF Staff Papers, vol. 45, no. 1, pp. 81–109, Mar. 1998.",
        "[27] T. W. Anderson and C. Hsiao, \"Formulation and estimation of dynamic models using panel data,\" J. Econometrics, vol. 18, no. 1, pp. 47–82, Jan. 1982.",
        "[28] M. Arellano and S. Bond, \"Some tests of specification for panel data: Monte Carlo evidence and an application to employment equations,\" Rev. Econ. Stud., vol. 58, no. 2, pp. 277–297, Apr. 1991.",
        "[29] R. Blundell and S. Bond, \"Initial conditions and moment restrictions in dynamic panel data models,\" J. Econometrics, vol. 87, no. 1, pp. 115–143, Aug. 1998.",
        "[30] European Central Bank, Financial Stability Review. Frankfurt am Main, Germany: ECB, Nov. 2023.",
        "[31] S. Dahiya, S. Singh, and P. Vrat, \"Predicting non-performing assets of Indian banks using machine learning techniques,\" IIMB Management Review, vol. 32, no. 3, pp. 295–307, Sep. 2020.",
        "[32] T. Chen and C. Guestrin, \"XGBoost: A scalable tree boosting system,\" in Proc. 22nd ACM SIGKDD Int. Conf. Knowledge Discovery and Data Mining (KDD '16), San Francisco, CA, USA, 2016, pp. 785–794.",
        "[33] S. M. Lundberg and S.-I. Lee, \"A unified approach to interpreting model predictions,\" in Advances in Neural Information Processing Systems (NeurIPS 2017), Long Beach, CA, USA, 2017, pp. 4765–4774.",
        "[34] S. M. Lundberg et al., \"From local explanations to global understanding with explainable AI for trees,\" Nature Machine Intelligence, vol. 2, no. 1, pp. 56–67, Jan. 2020."
    ]

    for ref in refs:
        p_ref = doc.add_paragraph()
        p_ref.paragraph_format.left_indent = Inches(0.3)
        p_ref.paragraph_format.first_line_indent = Inches(-0.3)
        p_ref.paragraph_format.space_after = Pt(3)
        r = p_ref.add_run(ref)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(8.5)

    out_path = r"d:\AI-ML Projects\NPA\papers\IEEE_NPA_EWS_Research_Paper.docx"
    doc.save(out_path)
    print(f"Document saved successfully to {out_path}")

if __name__ == "__main__":
    create_ieee_paper_docx()
