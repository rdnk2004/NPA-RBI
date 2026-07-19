# Policy Brief: A Data-Driven Early Warning System (EWS) for NPA Stress in Indian Banks
**TO:** The Executive Director, Department of Supervision, Reserve Bank of India
**FROM:** Young Professional (YP) Division, Macro-Financial Surveillance Unit
**DATE:** July 19, 2026
**SUBJECT:** Operationalizing a SupTech Early Warning System (EWS) using Econometric Panel Models, Explainable AI (SHAP), and Rigorously Validated Uncertainty Quantification

---

## 1. Executive Summary & Context

India's 2015–18 non-performing asset (NPA) crisis — where the Gross NPA (GNPA) ratio of Public Sector Banks (PSBs) spiked above 14% — showcased the severe costs of delayed supervisory action. In hindsight, bank-level vulnerabilities and macroeconomic deterioration were visible two years prior.

This policy brief presents a prototype SupTech Early Warning System (EWS) developed using public data from the RBI's *Report on Trend and Progress of Banking in India* (2010–2024) and macroeconomic indicators. It combines **Fixed Effects (FE) Panel Econometrics** with **Explainable AI (XGBoost + SHAP)** to identify the macro-financial drivers of asset quality stress, and a **probabilistic macro stress test** — calibrated to historical Indian banking shocks (IL&FS 2019, Post-AQR 2017, COVID FY21) — that reports confidence intervals and breach probabilities rather than single-number forecasts.

**A methodological finding shapes how this system should be used, and is stated here rather than left to Section 5.** Rigorous out-of-sample validation — walk-forward cross-validation across three independent time periods, benchmarked against naive baselines — shows that neither the FE model nor XGBoost meaningfully outperforms a simple "next year looks like this year" baseline at *point forecasting* next-year GNPA (Section 3, Finding 3). This is a direct, expected consequence of the sample size available (n=32 bank-group-years), not a flaw in either model's implementation. Accordingly, this EWS should be read and operationalized as a **driver-identification and scenario-risk tool**, not a precision forecasting instrument. Its supervisory value lies in (a) identifying which internal bank-health and macro variables move GNPA, and (b) quantifying the *probability* of a stress threshold breach under a defined macro scenario — both of which remain statistically defensible even where point forecasts are not. Recommendations in Section 4 are framed accordingly.

---

## 2. Data & Methodology

* **Data Sources:** RBI Report on Trend and Progress of Banking (RTP) Statistical Appendix (2010–2024) for bank-group indicators, and MOSPI/DBIE for macroeconomic variables.
* **Sample:** Panel dataset comprising 4 major bank groups — Public Sector Banks (PSBs), Private Sector Banks, Foreign Banks, and Small Finance Banks (SFBs) — covering the years 2013 to 2024 ($n = 32$ model-ready observations). **This sample is structurally unbalanced**: Foreign and Private banks contribute 12 years each (2013–2024), while PSB and SFB contribute only 4 years each (2021–2024), because these two categories are not reported as continuous series before 2018 in the source data (SFBs were only licensed from 2016 onward; PSB is reported here as a post-consolidation aggregate). This is a permanent characteristic of the published data, not a gap this analysis can close — see Finding 5.
* **Econometric Panel Model:** A Fixed Effects (FE) within-estimator controls for time-invariant group characteristics (e.g., PSBs' exposure to directed lending vs. Foreign Banks' cherry-picking strategies). The target is the GNPA ratio one year ahead ($t+1$):
  $$Y_{i, t+1} = \alpha_i + \beta_1 \text{ROA}_{i,t} + \beta_2 \text{PCR}_{i,t} + \beta_3 \text{CreditGrowth}_{i,t-2} + \gamma \textbf{Macro}_{t} + \epsilon_{i,t}$$
* **Explainable AI Layer:** A regularized, shallow XGBoost Regressor (maximum depth = 2, strong L1/L2 regularization) is trained to predict next-year GNPA. Predictions are interpreted using **SHAP (SHapley Additive exPlanations)** for supervisory-grade explainability of individual and global drivers.
* **Out-of-Sample Validation (new in this revision):** Both models are evaluated using **walk-forward (expanding-window) cross-validation**: the model is re-fit on all years up to a cutoff and tested only on the following year, repeated across three independent cutoffs (2022, 2023, 2024). This replaces evaluation on a single train/test split, which — with n=32 — is a single noisy draw rather than a stable estimate of performance.
* **Baseline Benchmarking (new in this revision):** Both models are compared, on identical folds, against three model-free baselines: **naive persistence** (predict next year = this year), **historical group mean**, and **pooled OLS** (same features, no fixed effects). This answers the question "is the added modeling complexity earning its keep?" directly, rather than assuming it.
* **Top-Down Stress Test with Uncertainty Quantification (new in this revision):** FE coefficients are used to project bank-group GNPA under three macro-stress scenarios (Mild/IL&FS 2019, Severe/Post-AQR 2017, Tail Risk/COVID FY21). In addition to the original point-estimate methodology, a **block bootstrap** (1,000 resamples, resampling each bank group's own years with replacement to preserve panel structure) is used to report a 90% confidence interval and an explicit **probability of breaching the RBI's PCA Risk Threshold 1 (6.0% GNPA)** for every bank group and scenario, rather than a single deterministic number.

---

## 3. Core Empirical Findings

### Finding 1: Econometric Drivers of Asset Quality Stress
The Fixed Effects panel model ($R^2_{\text{within}} = 0.650$, $n=32$) identifies internal bank-health metrics as the strongest correlates of future asset quality:
* **Return on Assets (ROA):** Coefficient of **$-2.333$**. A 1 percentage point (pp) decline in ROA is associated with a **2.33 pp increase** in next-year GNPA — declining profitability is the earliest internal supervisory warning signal in this model.
* **Provision Coverage Ratio (PCR):** Coefficient of **$-0.049$**. Lower provisioning buffers correlate with subsequent GNPA increases, consistent with weak provisioning acting as a precursor to recognized stress.
* **GDP Growth:** Coefficient of **$-0.075$**. Consistent with the well-documented countercyclicality of bad loans, a 1 pp drop in GDP growth is associated with a **0.075 pp** rise in next-year GNPA.
* **Credit Growth ($t-2$):** Coefficient of **$-0.028$** (not statistically significant in the multivariate model, despite a visible bivariate correlation). This suggests the credit boom's damage is mediated through subsequent ROA and GDP deterioration rather than acting as an independent linear driver.

**Interpretive caveat:** these coefficients describe *within-sample correlation structure*, not validated predictive power — see Finding 3. They remain useful for identifying *which* variables to monitor, independent of whether the resulting point forecast is reliable.

### Finding 2: Explainable AI & SHAP Global Importance
SHAP analysis of the XGBoost model identifies **ROA** as the single most influential feature, with a mean absolute contribution of **0.587 pp** to the predicted GNPA ratio, followed by PCR, and GDP growth and lagged credit growth in a near-tie for third:

```
Mean Absolute SHAP Value (Average impact on next-year GNPA prediction):
1. Return on Assets          ████████████████████████ 0.587 pp
2. Provision Coverage Ratio  █████████ 0.210 pp
3. GDP Growth                ███████ 0.165 pp
4. Credit Growth (t-2)       ███████ 0.165 pp
5. Repo Rate                 ███ 0.063 pp
6. CPI Inflation             █ 0.016 pp
```

This ranking corroborates Finding 1 independently: two different modeling approaches (linear panel regression and a non-parametric tree ensemble) converge on ROA and PCR as the dominant drivers. **This convergence — not the XGBoost point forecast itself — is the SHAP layer's real supervisory value**: it is a robustness check on which variables matter, obtained by a method with completely different assumptions than the FE model. (Note: credit growth and GDP growth are close enough in SHAP magnitude here that neither should be read as decisively more important than the other from this sample alone.)

### Finding 3: Out-of-Sample Validation — Neither Model Reliably Beats a Naive Baseline
This is the most important methodological finding in this brief, and the reason Section 1 leads with it.

Walk-forward cross-validation (three folds: test years 2022, 2023, 2024) was run for the FE model, XGBoost, and three model-free baselines, all evaluated on identical train/test splits:

| Model | Mean Absolute Error (pp) |
| :--- | :---: |
| **Naive (persistence: next year = this year)** | **1.04** |
| Pooled OLS (same features, no fixed effects) | 1.34 |
| XGBoost | ~1.06 |
| Fixed Effects (panel) | 1.60 |
| Historical group mean | 1.78 |

Two findings follow directly from this table:

1. **The Fixed Effects model — the primary econometric model in this brief — does not outperform simply assuming next year's GNPA equals this year's.** Its in-sample $R^2_{\text{within}}=0.650$ does not survive honest out-of-sample testing. This is a real, if uncomfortable, result: with $n=32$, the model has too little data to reliably learn a macro-driven forecasting relationship beyond what persistence already captures.
2. **XGBoost is roughly tied with the naive baseline**, and is materially more *stable* across folds than the FE model (a smaller spread in error across the three test years). Note that XGBoost's performance on any *single* train/test split (e.g. train ≤2021 / test ≥2022, the split used in earlier iterations of this analysis) can look considerably worse than this — that single split happens to include 2022, the hardest year to predict for every model tested, immediately following the COVID-19 shock. Walk-forward validation shows this was a property of that particular year, not of the model.

**Implication:** at the current sample size, none of the tested models should be relied upon for point-forecast accuracy beyond what a naive persistence assumption already provides. The FE and XGBoost models retain their value as **driver-identification tools** (Findings 1–2) and as the mechanism for the **probabilistic** stress test in Finding 4 — a fundamentally different, and more defensible, use of the same coefficients.

### Finding 4: Macro Stress Test — Point Estimates, Confidence Intervals, and Breach Probabilities
Applying macro shocks to the 2024 baseline via the FE coefficients yields the following point-estimate GNPA projections:

| Bank Group | Baseline (2024) | Mild Stress (IL&FS) | Severe Stress (Post-AQR) | Tail Risk (COVID FY21) |
| :--- | :---: | :---: | :---: | :---: |
| Foreign | 1.19% | 1.85% | 2.69% | 4.01% |
| **PSB** | 3.47% | 4.13% | 4.97% | **6.29%** |
| Private | 1.85% | 2.51% | 3.35% | 4.67% |
| SFB | 2.43% | 3.08% | 3.93% | 5.25% |

Given Finding 3, these point estimates alone would overstate this system's precision. A 1,000-draw block bootstrap of the same scenarios gives a 90% confidence interval and an explicit **probability of breaching the PCA Risk Threshold 1 (6.0%)** for each bank group and scenario:

| Bank Group | Scenario | Point (%) | 90% CI | Breach Probability |
| :--- | :--- | :---: | :---: | :---: |
| PSB | Mild Stress | 4.07 | [3.62, 4.36] | 0% |
| PSB | Severe Stress | 4.87 | [3.97, 5.50] | 1% |
| **PSB** | **Tail Risk** | **6.09** | **[4.40, 7.07]** | **64.3%** |
| SFB | Tail Risk | 5.05 | [3.35, 6.03] | 6.0% |
| Private | Tail Risk | 4.48 | [2.78, 5.45] | 1.3% |
| Foreign | Tail Risk | 3.82 | [2.12, 4.79] | 0% |

**This reframes the headline finding materially.** The earlier framing — "PSB marginally breaches the PCA threshold at 6.29% under Tail Risk" — implies a near-certain, precisely located outcome. The bootstrap-derived view is more accurate and more useful to a supervisor: **PSB carries roughly a 64% probability of breaching PCA Threshold 1 under a COVID-scale tail shock**, with a 90% plausible range spanning 4.40%–7.07%. A 64% breach probability under a tail scenario is a materially different — and arguably more actionable — statement than a marginal point-estimate breach, and should be communicated as such in any operational deployment.

### Finding 5: A Critical, Unresolvable Data Gap — PSB and SFB Have the Least History, and the Most Risk
PSB and SFB each contribute only **4 model-ready observations** (2021–2024) to this analysis, versus 12 each for Foreign and Private banks (2013–2024). This is not incidental: **PSB is simultaneously the bank group with the highest historical GNPA (mean 7.98% vs. 2.9–3.4% for the other three groups, per the full 2004–2025 series) and the group with the least data available to model that risk.** Every PSB-related estimate in this brief — including the 64.3% Tail Risk breach probability above — is flagged `LOW CONFIDENCE` in the underlying system and should be read with correspondingly wider interpretive caution than the Foreign/Private estimates.

This gap was investigated and confirmed to be a permanent feature of the publicly available RTP data (bank-group category definitions were not backfilled to earlier years), not an artifact of this analysis. It is reported here as a **finding in its own right**: current public offsite data provides the least statistical confidence in exactly the bank category that most needs supervisory attention. This has a direct implication for Recommendation 3, below.

---

## 4. Policy Recommendations

### Recommendation 1: Incorporate Sub-Sectoral EWS Thresholds
Aggregate bank-group GNPA is a lagging indicator. Data shows that sub-sectoral NPAs (e.g., Infrastructure, Iron & Steel, MSME) crossed 12% in 2013–14, well before the 2016 PSB aggregate spike.
* **Action:** The Department of Supervision should incorporate sector-specific early warning triggers. If infrastructure or MSME sector-level GNPA crosses **12%**, it should mandate a targeted credit audit of that sector's portfolio across all exposed banks, regardless of the bank's aggregate GNPA ratio.

### Recommendation 2: Operationalize Driver-Monitoring and Probabilistic Stress Testing — Not Point Forecasting
Given Finding 3, an operational deployment of this system should **not** present a single-number GNPA forecast as its primary output; doing so would imply a precision the validation results do not support.
* **Action:** Deploy the FE coefficients and SHAP driver rankings as a **monitoring dashboard** (which internal metrics are moving, and in which direction) combined with the **bootstrap-based breach-probability stress test** (Finding 4) as the primary risk signal. Re-run this methodology on granular, bank-level quarterly returns (DSB database) as they become available, which would also substantially increase the effective sample size and partially address Finding 5.

### Recommendation 3: Prioritize Closing the PSB/SFB Data Gap Before Trusting Group-Specific Signals
Finding 5 identifies a structural data gap that directly undermines confidence in the bank category most associated with historical NPA stress.
* **Action:** The Department of Supervision should assess whether bank-level (rather than group-aggregate) historical returns for constituent PSB entities can be reconstructed from DSB or individual bank annual reports prior to the 2017–2020 consolidation. Until this is done, any PSB-specific output from this or a similar system should be presented alongside an explicit low-confidence flag, as implemented in this prototype.

---

## 5. Supervisory Limitations of the Model

1. **Neither model reliably beats a naive baseline at point forecasting (Finding 3).** This is the most important limitation in this brief and should govern how any output is used: as driver-identification and scenario-probability evidence, not as a precise GNPA forecast.
2. **Structural data imbalance (Finding 5):** PSB and SFB contribute only 4 observations each, versus 12 for Foreign/Private, and this cannot be resolved with the currently available public data.
3. **Aggregated Public Data:** This EWS uses bank-group level data and cannot detect idiosyncratic risk within a single institution hidden inside an aggregate (e.g., one weak private bank within the aggregate private-sector statistics).
4. **Small Sample Size:** At $n=32$ total observations, both the FE and XGBoost models have limited statistical power and limited ability to generalize to structural regimes not represented in 2013–2024 (e.g., a shock materially different in character from IL&FS, AQR, or COVID).
5. **Annual Frequency:** Annual reporting introduces a reporting lag; quarterly or monthly DSB returns would be required for real-time supervisory action, and would also help address Limitation 2 by increasing the effective sample size per bank group.

---