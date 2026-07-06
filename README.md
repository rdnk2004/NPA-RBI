# RBI NPA Early Warning System (EWS) — SupTech Prototype

This repository contains a prototype **SupTech Early Warning System (EWS)** designed to replicate and enhance the offsite surveillance methodologies used by the Reserve Bank of India (RBI) to monitor asset quality stress. 

Using public banking sector panel data and macroeconomic variables, this system predicts Gross Non-Performing Asset (GNPA) ratios at a 1-year forward horizon. It integrates **econometric panel models** with **regularized machine learning (XGBoost)** and **explainable AI (SHAP)**, validated through a top-down macroeconomic stress test.

---

## 📂 Repository Structure

* **`datasets/`**: Master panel datasets merging bank-group level metrics with macroeconomic variables.
  * [banking_panel.csv](file:///d:/NPA/datasets/banking_panel.csv): Panel data (year × bank_group).
  * [macro_annual.csv](file:///d:/NPA/datasets/macro_annual.csv): Annual macroeconomic indicators (GDP, Repo Rate, CPI).
* **`notebooks/`**: Analytical pipeline executed in chronological order:
  * [01_data_prep.ipynb](file:///d:/NPA/notebooks/01_data_prep.ipynb): Data ingestion and forward-lag target engineering.
  * [02_eda.py](file:///d:/NPA/notebooks/02_eda.py): Visualizing the India NPA cycle (2004–2025), credit growth vs. NPA lag, and PCR trends.
  * [03_panel_regression.py](file:///d:/NPA/notebooks/03_panel_regression.py): Fixed Effects (FE) panel regression (econometric baseline).
  * [04_xgboost_shap.py](file:///d:/NPA/notebooks/04_xgboost_shap.py): Shallow XGBoost Regressor with global and individual SHAP explanations.
  * [05_stress_test.py](file:///d:/NPA/notebooks/05_stress_test.py): Macroeconomic stress testing and PCA threshold breach validation.
* **`outputs/`**: Generated charts (forest plots, SHAP beeswarms, force plots, actual-vs-predicted scatter plots, stress heatmap, and traffic-light supervisory tables).
* **`policy_note/`**: 
  * [npa_ews_policy_brief.md](file:///d:/NPA/policy_note/npa_ews_policy_brief.md): A formal policy memorandum addressed to the Department of Supervision detailing findings, recommendations, and limitations.

---

## 📈 Core Findings

### 1. Econometric Drivers (Fixed Effects Panel Model)
* **Return on Assets (ROA)** is the single strongest leading indicator of future asset quality. A **1 pp drop** in ROA is associated with a **$2.33$ pp rise** in next-year GNPA ($p < 0.01$).
* **Provision Coverage Ratio (PCR)** is statistically significant ($p < 0.05$), showing that weak provisioning buffers correlate with subsequent spikes in NPA defaults.
* **GDP Growth** exhibits strong countercyclical effects ($p < 0.10$), adding **$0.075$ pp** to GNPA for every 1 pp slowdown in macroeconomic output.
* **Credit Growth ($t-2$)** exhibits a strong bivariate leading relationship with NPAs, reflecting the lag of term-loan default cycles.

### 2. Machine Learning Explainability (SHAP Value Analysis)
Using a regularized XGBoost model (max depth = 2), SHAP analysis identifies **ROA** as the dominant predictive feature (mean absolute contribution of **$0.546$ pp** to predictions), followed by PCR and GDP growth. EWS force plots show that declining ROA combined with falling PCR would have flagged the PSB stress of 2015–18 nearly two years in advance.

### 3. EWS Offsite Surveillance Dashboard (2025 Outlook)
Using 2024 actuals, the XGBoost EWS predicts the following outlook for 2025, placing all bank groups on an **ELEVATED** watch status due to cumulative lag compression in ROA:
* **Public Sector Banks (PSBs):** Projected GNPA = **$4.84\%$** (2024 Actual = $3.47\%$)
* **Private Sector Banks:** Projected GNPA = **$3.70\%$** (2024 Actual = $1.85\%$)
* **Small Finance Banks (SFBs):** Projected GNPA = **$3.57\%$** (2024 Actual = $2.43\%$)
* **Foreign Banks:** Projected GNPA = **$3.56\%$** (2024 Actual = $1.19\%$)

### 4. Macro Stress Test (PCA Breaches)
Applying macroeconomic shocks calibrated to historical Indian banking crises yields:

| Bank Group | Baseline (2024 Actual) | Mild Stress (IL&FS 2019) | Severe Stress (Post-AQR 2017) | Tail Risk (COVID FY21) |
| :--- | :---: | :---: | :---: | :---: |
| **Foreign** | 1.19% | 1.85% | 2.69% | 4.01% |
| **PSB** | 3.47% | 4.13% | 4.97% | **6.29%** |
| **Private** | 1.85% | 2.51% | 3.35% | 4.67% |
| **SFB** | 2.43% | 3.08% | 3.93% | 5.25% |

*Under the Tail Risk scenario (mirroring the COVID-19 GDP contraction of $-4.3\%$), PSB GNPA rises to **$6.29\%$**, marginally breaching the RBI’s Prompt Corrective Action (PCA) Risk Threshold 1 of $6.0\%$, highlighting residual vulnerability.*

---

## 🛠️ How to Run

### Prerequisite Packages
Install the required econometric, machine learning, and visualization libraries:
```bash
pip install pandas numpy matplotlib seaborn statsmodels scikit-learn xgboost shap linearmodels openpyxl requests scipy
```

### Execution Order
Run the python files in the following order from the `notebooks/` directory to generate the datasets and outputs:
```bash
cd notebooks
python 02_eda.py
python 03_panel_regression.py
python 04_xgboost_shap.py
python 05_stress_test.py
```

---

## 🏛️ Policy Recommendations

1. **Sub-Sectoral EWS Triggers:** Implement sector-specific offsite surveillance thresholds (e.g. Infrastructure or MSME) triggering reviews when sub-sector NPA exceeds **$12\%$**, preventing lagging aggregate indicators from masking risk.
2. **SupTech Dashboard Operationalization:** Re-train this XGBoost + SHAP model framework on quarterly bank-level supervisory returns (DSB database) to provide offsite examiners with auditable, individual risk contribution metrics.
