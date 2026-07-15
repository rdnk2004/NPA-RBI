# RBI NPA Early Warning System (EWS) — SupTech Prototype

![CI](https://github.com/rdnk2004/NPA-RBI/actions/workflows/ci.yml/badge.svg)

This repository contains a prototype **SupTech Early Warning System (EWS)** designed to replicate and enhance the offsite surveillance methodologies used by the Reserve Bank of India (RBI) to monitor asset quality stress. 

Using public banking sector panel data and macroeconomic variables, this system predicts Gross Non-Performing Asset (GNPA) ratios at a 1-year forward horizon. It integrates **econometric panel models** with **regularized machine learning (XGBoost)** and **explainable AI (SHAP)**, validated through a top-down macroeconomic stress test.

---

## 📂 Repository Structure

* **`src/npa_ews/`**: Installable Python package — the tested, reusable core logic.
  * `config.py`: Single source of truth for feature lists, paths, bank-group colors, and stress scenario definitions (previously duplicated across every notebook).
  * `data.py`: Panel loading with explicit schema validation (column checks, plausible-range checks, duplicate detection) — fails loudly on bad data instead of silently proceeding.
  * `models/panel_fe.py`: Fixed-effects panel regression as a reusable class.
  * `models/xgb_model.py`: XGBoost + SHAP wrapper with a clean fit/predict/explain interface.
  * `stress.py`: Macro stress scenario application and PCA-threshold breach detection.
  * `cli.py`: `npa-ews run` command-line entrypoint tying the pipeline together with structured logging.
* **`tests/`**: `pytest` suite (21 tests) covering schema validation, the fixed-effects transform, stress test arithmetic, and — most importantly — **leakage checks**: verifying the train/test temporal split doesn't overlap, the target isn't a disguised feature, and the target really is forward-shifted rather than a same-year copy.
* **`.github/workflows/ci.yml`**: Runs lint (`ruff`), the full test suite with coverage, and an end-to-end pipeline smoke test on every push, across Python 3.10–3.12.
* **`datasets/`**: Master panel datasets merging bank-group level metrics with macroeconomic variables.
  * `banking_panel.csv`: Panel data (year × bank_group).
  * `macro_annual.csv`: Annual macroeconomic indicators (GDP, Repo Rate, CPI).
* **`notebooks/`**: Original exploratory/chart-generation scripts (`01`–`05`), kept for the full EDA and figure generation. The modeling logic they contain has been extracted into `src/npa_ews/` above; these now serve mainly as the visualization/reporting layer.
* **`outputs/`**: Generated charts (forest plots, SHAP beeswarms, force plots, actual-vs-predicted scatter plots, stress heatmap, and traffic-light supervisory tables).
* **`policy_note/`**:
  * `npa_ews_policy_brief.md`: A formal policy memorandum addressed to the Department of Supervision detailing findings, recommendations, and limitations.

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

### Install
Install the package in editable mode (pulls in all modeling/viz dependencies from `pyproject.toml`):
```bash
pip install -e ".[dev]"
```

### Run the pipeline
```bash
npa-ews run                # full pipeline: FE regression + XGBoost + stress test
npa-ews run --stage fe      # just the fixed-effects regression
npa-ews run --stage xgb     # just XGBoost + SHAP
npa-ews run --stage stress  # just the macro stress test
```

### Run the tests
```bash
pytest tests/ -v --cov=npa_ews --cov-report=term-missing
```

### Regenerate charts and figures
The original chart-generation scripts still work, now importing shared logic from `src/npa_ews/` instead of redefining it:
```bash
cd notebooks
python 02_eda.py
python 03_panel_regression.py
python 04_xgboost_shap.py
python 05_stress_test.py
```

### A note on model performance
The XGBoost model's **test-set R² is -0.495** — worse than simply predicting the mean. This is expected, not a bug: with ~32 usable observations, XGBoost's value here is as a **pattern-identifier** (via SHAP) that cross-checks the fixed-effects regression's drivers, not as a standalone forecaster. The fixed-effects model (R² = 0.650, n = 32) is the model actually used for the stress test in `stress.py`. See `tests/test_no_leakage.py` for the checks that verify this isn't a leakage artifact in either direction.

---

## 🏛️ Policy Recommendations

1. **Sub-Sectoral EWS Triggers:** Implement sector-specific offsite surveillance thresholds (e.g. Infrastructure or MSME) triggering reviews when sub-sector NPA exceeds **$12\%$**, preventing lagging aggregate indicators from masking risk.
2. **SupTech Dashboard Operationalization:** Re-train this XGBoost + SHAP model framework on quarterly bank-level supervisory returns (DSB database) to provide offsite examiners with auditable, individual risk contribution metrics.
