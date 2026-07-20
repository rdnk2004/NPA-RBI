# RBI NPA Early Warning System (EWS) — SupTech Prototype

![CI](https://github.com/rdnk2004/NPA-RBI/actions/workflows/ci.yml/badge.svg)

This repository contains a prototype **SupTech Early Warning System (EWS)** designed to replicate and enhance the offsite surveillance methodologies used by the Reserve Bank of India (RBI) to monitor asset quality stress. 

Using public banking sector panel data and macroeconomic variables, this system identifies the macro-financial drivers of asset quality stress and quantifies bank-group risk under macro stress scenarios. It integrates **econometric panel models** with **regularized machine learning (XGBoost)** and **explainable AI (SHAP)** for driver identification, backed by a **probabilistic macro stress test** that reports confidence intervals and breach probabilities rather than single-number forecasts — and by rigorous out-of-sample validation that's honest about what this system can and can't predict (see Core Findings §3 below).

---

## 📂 Repository Structure

* **`src/npa_ews/`**: Installable Python package — the tested, reusable core logic.
  * `config.py`: Single source of truth for feature lists, paths, bank-group colors, and stress scenario definitions (previously duplicated across every notebook).
  * `data.py`: Panel loading with explicit schema validation (column checks, plausible-range checks, duplicate detection), plus per-bank-group **data-sufficiency flagging** — groups with too few observations (e.g. PSB/SFB, see Core Findings §4) are tagged `LOW CONFIDENCE` everywhere their numbers appear.
  * `models/panel_fe.py`: Fixed-effects panel regression, including out-of-sample prediction via recovered group intercepts (needed for cross-validation).
  * `models/xgb_model.py`: XGBoost + SHAP wrapper with a clean fit/predict/explain interface.
  * `validation.py`: Walk-forward (expanding-window) cross-validation, and a baseline comparison against naive/mean/pooled-OLS predictors — the honest answer to "is this model actually worth it?"
  * `stress.py`: Macro stress scenario application, PCA-threshold breach detection, and block-bootstrap confidence intervals + breach probabilities.
  * `cli.py`: `npa-ews run` command-line entrypoint tying the pipeline together with structured logging.
* **`tests/`**: `pytest` suite (41 tests) covering schema validation, the fixed-effects transform, stress test arithmetic, walk-forward CV integrity, baseline-comparison correctness, data-reliability flagging, and — most importantly — **leakage checks**: verifying the train/test temporal split doesn't overlap, the target isn't a disguised feature, and the target really is forward-shifted rather than a same-year copy.
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

*The highlights below are a snapshot of the results. For full methodology, statistical detail, limitations, and policy recommendations, see the [complete policy brief](policy_note/npa_ews_policy_brief.md).*

### 1. Econometric Drivers (Fixed Effects Panel Model)
* **Return on Assets (ROA)** is the single strongest leading indicator of future asset quality. A **1 pp drop** in ROA is associated with a **$2.33$ pp rise** in next-year GNPA ($p < 0.01$).
* **Provision Coverage Ratio (PCR)** is statistically significant ($p < 0.05$), showing that weak provisioning buffers correlate with subsequent spikes in NPA defaults.
* **GDP Growth** exhibits strong countercyclical effects ($p < 0.10$), adding **$0.075$ pp** to GNPA for every 1 pp slowdown in macroeconomic output.
* **Credit Growth ($t-2$)** exhibits a strong bivariate leading relationship with NPAs, reflecting the lag of term-loan default cycles.

### 2. Machine Learning Explainability (SHAP Value Analysis)
Using a regularized XGBoost model (max depth = 2), SHAP analysis identifies **ROA** as the dominant predictive feature (mean absolute contribution of **$0.546$ pp** to predictions), followed by PCR and GDP growth. EWS force plots show that declining ROA combined with falling PCR would have flagged the PSB stress of 2015–18 nearly two years in advance.

### 3. Out-of-Sample Validation — Is This Actually Worth It?
Rather than trust a single train/test split, every model here is evaluated with **walk-forward cross-validation** (re-fit on all years up to a cutoff, test only on the next year, repeated across 3 independent cutoffs) and benchmarked against model-free baselines on identical folds:

| Model | Mean Absolute Error (pp) |
| :--- | :---: |
| **Naive (persistence: next year = this year)** | **1.04** |
| Pooled OLS (no fixed effects) | 1.34 |
| XGBoost | 1.06 |
| Fixed Effects (panel) | 1.60 |
| Historical group mean | 1.78 |

**Honest takeaway: neither the Fixed Effects model nor XGBoost meaningfully beats just assuming next year looks like this year.** This is a direct, expected consequence of n=32 — not a bug in either model. XGBoost is roughly tied with the naive baseline and noticeably more *stable* across folds than the Fixed Effects model; the FE model's in-sample R²=0.650 does not survive out-of-sample testing. Practical implication: **this system's value is driver identification (§1–2) and probabilistic scenario risk (§4), not point-forecasting** — see the [policy brief](policy_note/npa_ews_policy_brief.md) (Finding 3) for the full validation detail. Run `npa-ews run --stage validate` to reproduce this table.

### 4. Macro Stress Test — Point Estimates, Confidence Intervals, and Breach Probabilities
Applying macroeconomic shocks calibrated to historical Indian banking crises to the FE coefficients yields the following point estimates:

| Bank Group | Baseline (2024 Actual) | Mild Stress (IL&FS 2019) | Severe Stress (Post-AQR 2017) | Tail Risk (COVID FY21) | Data Confidence |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Foreign** | 1.19% | 1.85% | 2.69% | 4.01% | reliable (n=12) |
| **PSB** | 3.47% | 4.13% | 4.97% | **6.29%** | ⚠️ LOW (n=4) |
| **Private** | 1.85% | 2.51% | 3.35% | 4.67% | reliable (n=12) |
| **SFB** | 2.43% | 3.08% | 3.93% | 5.25% | ⚠️ LOW (n=4) |

Given §3 above, point estimates alone overstate this system's precision. A 1,000-draw block bootstrap gives a 90% confidence interval and explicit **probability of breaching the PCA Risk Threshold 1 (6.0% GNPA)**:

| Bank Group | Scenario | Point (%) | 90% CI | Breach Probability |
| :--- | :--- | :---: | :---: | :---: |
| **PSB** | **Tail Risk** | **6.09** | **[4.40, 7.07]** | **64.3%** |
| SFB | Tail Risk | 5.05 | [3.35, 6.03] | 6.0% |
| Private | Tail Risk | 4.48 | [2.78, 5.45] | 1.3% |
| Foreign | Tail Risk | 3.82 | [2.12, 4.79] | 0% |

*"PSB marginally breaches at 6.29%" implies a near-certain, precisely located outcome. The bootstrap view is more honest: **PSB carries roughly a 64% probability of breaching PCA Threshold 1 under a COVID-scale tail shock**, with a 90% plausible range of 4.40%–7.07%. Note PSB's number is also flagged low-confidence (n=4) — see below.*

### 5. A Data Gap That Can't Be Fixed With Better Modeling
PSB and SFB each have only **4 model-ready observations** (2021–2024), vs. 12 each for Foreign/Private (2013–2024) — because these categories aren't reported as continuous series before 2018 in the source RBI data (SFBs licensed from 2016; PSB reported as a post-consolidation aggregate). **PSB is simultaneously the highest-risk group (mean GNPA 7.98% vs. 2.9–3.4% for the others) and the group with the least data to model that risk** — confirmed as a permanent feature of the public data, not something this analysis can close. Every PSB estimate above is tagged `LOW CONFIDENCE` automatically by `data.group_reliability()`, not as a manual afterthought.

---

## 🛠️ How to Run

### Install
Install the package in editable mode (pulls in all modeling/viz dependencies from `pyproject.toml`):
```bash
pip install -e ".[dev]"
```

### Run the pipeline
```bash
npa-ews run                # full pipeline: FE regression + XGBoost + stress test + validation
npa-ews run --stage fe        # just the fixed-effects regression
npa-ews run --stage xgb       # just XGBoost + SHAP
npa-ews run --stage stress    # just the macro stress test
npa-ews run --stage validate  # walk-forward CV + naive/mean/OLS/XGBoost comparison
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
Neither the Fixed Effects model nor XGBoost meaningfully beats a naive "next year = this year" baseline under walk-forward cross-validation (see Core Findings §3). This is expected, not a bug, given ~32 usable observations. The earlier single-split evaluation (train ≤2021, test ≥2022) made XGBoost look considerably worse than this — that split happened to include 2022, the hardest year to predict for every model tested, right after COVID. See `tests/test_no_leakage.py` and `tests/test_baselines.py` for the checks behind this.

---

## 🏛️ Policy Implications

This prototype doesn't stop at a model — its findings are written up as a formal policy brief addressed to RBI's Department of Supervision, covering methodology, empirical findings, limitations, and concrete recommendations (sub-sectoral EWS triggers, quarterly bank-level dashboard operationalization).

📄 **[Read the full policy brief →](policy_note/npa_ews_policy_brief.md)**
