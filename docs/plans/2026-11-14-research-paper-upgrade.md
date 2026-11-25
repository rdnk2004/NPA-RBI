# Hybrid SupTech EWS & Bank-Level Asset Quality Research Paper Implementation Plan

> **For Agent:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Transform the NPA Early Warning System from an aggregated 32-row toy model into a publication-grade, two-tier empirical research system (Restored Macro Bank-Group Panel + Granular Bank-Level Panel of 40+ banks over 2005–2024), pairing Dynamic Panel Econometrics with Explainable Machine Learning and Logit Macro-Stress Testing.

**Architecture:**
- **Data Layer:** Reconstruct uninterrupted 2005–2024 historical series for Public Sector Banks (fixing the pre-2018 SBI + Nationalised Banks aggregation bug) and synthesize a granular bank-level panel ($N \approx 750+$ observations) from raw RBI tables (`F4_GNPA.xlsx`, `F5_T11.xlsx`, `F3_CRAR.xlsx`, `F7_NPA_MOVEMENT.xlsx`, `F2_ECON.xlsx`).
- **Econometric Layer:** Replace static within-estimator with Dynamic Panel Estimation (First-Difference / IV-GMM) addressing NPA persistence ($\alpha \approx 0.7$) and Nickell bias.
- **Machine Learning Layer:** Walk-forward regularized tree ensembles (XGBoost/LightGBM) predicting continuous GNPA ratios and Prompt Corrective Action (PCA) threshold breaches with TreeSHAP attributions.
- **Stress-Testing Layer:** Logit-transformed macro-satellite stress models projecting non-linear GNPA and Tier-1 CRAR capital depletion under historical crisis scenarios.
- **Manuscript Layer:** Author a complete, submission-ready academic paper manuscript adhering to international journal standards (*Journal of Banking & Finance* / *Expert Systems with Applications*).

**Tech Stack:** Python 3.11, pandas, numpy, openpyxl, linearmodels, statsmodels, scikit-learn, xgboost, shap, fastapi, streamlit, pytest.

---

### Task 1: Environment & Repository Hygiene

**Files:**
- Modify: `.gitignore`

**Step 1: Write the change**
Add `.cache/` and `papers/` to `.gitignore`.

**Step 2: Commit**
`git commit -m "chore: add .cache to .gitignore"`

---

### Task 2: Data Extraction & Dual-Panel Construction

**Files:**
- Create: `src/npa_ews/data_builder.py`
- Modify: `datasets/banking_panel.csv` (regenerated with full 2005–2024 PSB series)
- Create: `datasets/bank_level_panel.csv` (granular bank-level longitudinal panel)
- Test: `tests/test_data_builder.py`

**Step 1: Write test for data builder**
Verify that:
1. `datasets/banking_panel.csv` has PSB data starting from 2005 (not 2018).
2. PSB GNPA ratio in 2016–2018 is > 10% (capturing the true AQR peak).
3. `datasets/bank_level_panel.csv` contains >= 35 unique banks with >= 15 years of data each.

**Step 2: Run test to verify it fails**
`pytest tests/test_data_builder.py -v`

**Step 3: Implement data_builder.py**
Write the data extraction engine that:
1. Correctly aggregates `STATE BANK OF INDIA AND ITS ASSOCIATES` + `NATIONALISED BANKS` into `PSB` for 2004–2017 in `F4_GNPA.xlsx`.
2. Extracts individual banks from `F4_GNPA.xlsx`, `F5_T11.xlsx` (ROA, CD ratio), `F3_CRAR.xlsx` (CRAR), and `F7_NPA_MOVEMENT.xlsx` (PCR, write-offs).
3. Merges macroeconomic time series from `F2_ECON.xlsx`.
4. Saves both `banking_panel.csv` (restored macro) and `bank_level_panel.csv` (micro panel).

**Step 4: Run test to verify it passes**
`pytest tests/test_data_builder.py -v`

**Step 5: Commit**
`git commit -m "feat(data): restore 20-year PSB history and build bank-level longitudinal panel"`

---

### Task 3: Data Loading & Schema Validation Updates

**Files:**
- Modify: `src/npa_ews/config.py`
- Modify: `src/npa_ews/data.py`
- Test: `tests/test_data.py`

**Step 1: Write failing tests in test_data.py**
Verify `load_bank_level_panel()` loads valid columns, checks ranges, and handles bank entity names.

**Step 2: Run test to verify failure**
`pytest tests/test_data.py -k "bank_level" -v`

**Step 3: Implement functions in config.py and data.py**
Add `BANK_LEVEL_PANEL_CSV`, feature constants for bank-level models, and `load_bank_level_panel()`.

**Step 4: Run tests to verify pass**
`pytest tests/test_data.py -v`

**Step 5: Commit**
`git commit -m "feat(data): add bank-level panel loading and validation schema"`

---

### Task 4: Dynamic Panel Econometric Engine (Nickell Bias Resolution)

**Files:**
- Create: `src/npa_ews/models/dynamic_panel.py`
- Test: `tests/test_dynamic_panel.py`

**Step 1: Write failing test in test_dynamic_panel.py**
Test dynamic panel estimation using `linearmodels` (PanelOLS with entity effects, and FirstDifferenceOLS / Instrumental Variables for lagged GNPA).

**Step 2: Run test to verify failure**
`pytest tests/test_dynamic_panel.py -v`

**Step 3: Implement dynamic_panel.py**
1. Implement `DynamicPanelModel` that estimates:
   $$logit(GNPA_{i,t}) = \alpha \cdot logit(GNPA_{i,t-1}) + \beta X_{i,t} + \mu_i + \epsilon_{i,t}$$
2. Recover economic elasticities for ROA, Credit Growth ($t-2$), CRAR, and GDP growth.
3. Compare against static within-estimator to demonstrate why dynamic estimation is theoretically required.

**Step 4: Run test to verify pass**
`pytest tests/test_dynamic_panel.py -v`

**Step 5: Commit**
`git commit -m "feat(econometrics): implement dynamic panel asset quality estimator"`

---

### Task 5: Upgraded Machine Learning & Prompt Corrective Action (PCA) Classification

**Files:**
- Modify: `src/npa_ews/models/xgb_model.py`
- Modify: `src/npa_ews/validation.py`
- Test: `tests/test_xgb_bank_level.py`

**Step 1: Write failing tests**
Verify XGBoost training and walk-forward cross-validation on the bank-level panel ($N > 500$), checking out-of-sample MAE, RMSE, and PCA breach AUC-ROC.

**Step 2: Run test to verify failure**
`pytest tests/test_xgb_bank_level.py -v`

**Step 3: Implement model enhancements**
1. Train XGBoost on bank-level features with expanding window CV.
2. Add binary/multi-class classification for RBI PCA Threshold breaches (GNPA > 6.0%, > 9.0%, > 12.0%).
3. Compute TreeSHAP attributions for high-stress banks vs. resilient banks.

**Step 4: Run test to verify pass**
`pytest tests/test_xgb_bank_level.py -v`

**Step 5: Commit**
`git commit -m "feat(ml): implement bank-level XGBoost and PCA breach classification"`

---

### Task 6: Non-Linear Macroprudential Stress Testing & Capital Depletion

**Files:**
- Modify: `src/npa_ews/stress.py`
- Test: `tests/test_stress.py`

**Step 1: Write tests for logit satellite stress testing**
Verify bounded GNPA projections $\in [0, 100\%]$ and CRAR capital depletion.

**Step 2: Implement logit stress engine**
1. Translate scenario macro shocks via logit transformation.
2. Calculate post-stress provision requirement and depleted CRAR:
   $$CRAR_i^{\text{stressed}} = CRAR_i - \frac{\Delta GNPA_i \times PCR_i \times Advances_i}{RWA_i}$$
3. Count regulatory capital breaches (CRAR < 9.0%).

**Step 3: Run test to verify pass**
`pytest tests/test_stress.py -v`

**Step 4: Commit**
`git commit -m "feat(stress): implement logit satellite stress model and capital depletion analysis"`

---

### Task 7: Update API and Frontend Serving Layer

**Files:**
- Modify: `src/npa_ews/schemas.py`
- Modify: `src/npa_ews/api.py`
- Modify: `frontend/client.py`
- Modify: `frontend/app.py`
- Test: `tests/test_api.py`

**Step 1: Update API schemas and routes**
Expose both `/drivers` (macro & micro), `/stress/bank-level`, and `/pca-breaches`.

**Step 2: Run test suite**
Verify all API endpoints return valid typed responses.

**Step 3: Commit**
`git commit -m "feat(api): expose dual-tier macro and bank-level supervisory endpoints"`

---

### Task 8: Author Full Academic Research Paper Manuscript

**Files:**
- Create: `papers/npa_ews_research_paper.md`
- Create: `papers/tables/` (empirical output tables)

**Step 1: Author complete publication-ready manuscript**
Structure:
1. Abstract & JEL Classification (G21, G28, C23, C53)
2. Introduction: Indian Banking Crisis, Regulatory Forbearance, and SupTech
3. Theoretical Framework & Comprehensive Literature Review
4. Data Reconstruction & Variable Construction (2005–2024 Panel)
5. Econometric Methodology: Dynamic Panel System GMM vs. Static Within-Estimator
6. Machine Learning Architecture: Regularized Tree Ensembles & XAI (SHAP)
7. Macroprudential Stress Testing & Capital Depletion Simulation
8. Empirical Results, Robustness Checks, and Model Comparison
9. Supervisory Policy Implications & Operationalization
10. References (Comprehensive academic citations)

**Step 2: Verify all numbers match computed empirical outputs**

**Step 3: Commit**
`git commit -m "docs(research): author comprehensive peer-reviewed research paper manuscript"`
