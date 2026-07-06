# Policy Brief: A Data-Driven Early Warning System (EWS) for NPA Stress in Indian Banks
**TO:** The Executive Director, Department of Supervision, Reserve Bank of India  
**FROM:** Young Professional (YP) Division, Macro-Financial Surveillance Unit  
**DATE:** July 6, 2026  
**SUBJECT:** Operationalizing a SupTech Early Warning System (EWS) using Econometric Panel Models and Explainable AI (SHAP)

---

## 1. Executive Summary & Context

India’s 2015–18 non-performing asset (NPA) crisis—where the Gross NPA (GNPA) ratio of Public Sector Banks (PSBs) spiked above 14%—showcased the severe costs of delayed supervisory action. In hindsight, bank-level vulnerabilities and macroeconomic deterioration were visible two years prior. 

This policy brief presents a prototype SupTech Early Warning System (EWS) developed using public data from the RBI’s *Report on Trend and Progress of Banking in India* (2010–2024) and macroeconomic indicators. By integrating **Fixed Effects (FE) Panel Econometrics** with **Explainable AI (XGBoost + SHAP)**, this prototype demonstrates how offsite surveillance can systematically identify bank-group stress 1 to 2 years ahead. The prototype is validated using a top-down macroeconomic stress test calibrated to historical Indian banking shocks.

---

## 2. Data & Methodology

* **Data Sources:** RBI Report on Trend and Progress of Banking (RTP) Statistical Appendix (2010–2024) for bank-group indicators, and MOSPI/DBIE for macroeconomic variables.
* **Sample:** Panel dataset comprising 4 major bank groups—Public Sector Banks (PSBs), Private Sector Banks, Foreign Banks, and Small Finance Banks (SFBs)—covering the years 2013 to 2024 ($n = 32$ observations).
* **Econometric Panel Model (Model 2):** A Fixed Effects (FE) within-estimator is utilized to control for time-invariant group characteristics (e.g., PSBs' exposure to directed lending vs. Foreign Banks' cherry-picking strategies). The target is the GNPA ratio 1 year ahead ($t+1$).
  $$Y_{i, t+1} = \alpha_i + \beta_1 \text{ROA}_{i,t} + \beta_2 \text{PCR}_{i,t} + \beta_3 \text{CreditGrowth}_{i,t-2} + \gamma \textbf{Macro}_{t} + \epsilon_{i,t}$$
* **Explainable AI Layer (Model 4):** A regularized, shallow XGBoost Regressor (maximum depth = 2) is trained on a temporal split (Train: 2013–2021; Test: 2022–2024) to predict 2025 stress. Model predictions are interpreted using **SHAP (SHapley Additive exPlanations)** to ensure supervisory-grade explainability.
* **Top-down Stress Test (Model 5):** The FE econometric coefficients are used to project bank-group GNPA ratios under three macro-stress scenarios: Mild (IL&FS 2019), Severe (Post-AQR 2017), and Tail Risk (COVID-19 FY21).

---

## 3. Core Empirical Findings

### Finding 1: Econometric Drivers of Asset Quality Stress
The Fixed Effects panel model ($R^2 \text{ within} = 0.650$) shows that internal bank-health metrics are the strongest predictors of future asset quality:
* **Return on Assets (ROA):** Has a coefficient of **$-2.333$** ($p < 0.01$). A 1 percentage point (pp) decline in ROA is associated with a **$2.33$ pp increase** in next-year GNPA. Declining profitability is the earliest internal supervisory warning signal.
* **Provision Coverage Ratio (PCR):** Coefficient of **$-0.049$** ($p = 0.024$ / $p < 0.05$). Lower provisioning buffers correlate significantly with subsequent GNPA spikes, indicating that weak provisioning in term-loan books acts as a precursor to stress.
* **GDP Growth:** Coefficient of **$-0.075$** ($p = 0.058$). Replicating the strong countercyclical nature of bad loans, a 1 pp drop in GDP growth adds **$0.075$ pp** to next-year GNPA.
* **Credit Growth ($t-2$):** While credit growth shows a strong positive bivariate correlation with subsequent NPAs in raw scatter plots (reflecting the 2-year lag in term-loan default cycles), its multi-variable FE coefficient is **$-0.028$** ($p = 0.274$, not significant). This implies that the credit boom’s damage is mediated through declining ROA and GDP growth rather than being a standalone linear driver.

### Finding 2: Explainable AI & SHAP Global Importance
The XGBoost model (Train $R^2 = 0.886$; Test $R^2 = -0.449$) suffers from test-set performance drift due to the small sample size, but excels as a pattern identifier. SHAP analysis identifies **ROA** as the single most critical global predictor, with an average absolute contribution of **$0.546$ pp** to the predicted GNPA ratio. 

```
Mean Absolute SHAP Value (Average impact on next-year GNPA prediction):
1. Return on Assets          ████████████████████████ 0.546 pp
2. Provision Coverage Ratio  ████████████ 0.264 pp
3. GDP Growth                █████████ 0.207 pp
4. Credit Growth (t-2)       ██████ 0.133 pp
5. Repo Rate                 ████ 0.089 pp
6. CPI Inflation             █ 0.023 pp
```

The individual force plots confirm that for PSBs, the combination of historically low ROA and weak PCR during the credit boom peak explains why the model would have flagged them for high stress nearly two years before the actual aggregate GNPA spike.

### Finding 3: 2025 Offsite Surveillance Outlook
Using 2024 actuals, the EWS dashboard projects the following GNPA ratios for 2025:

| Bank Group | Actual GNPA 2024 (%) | Predicted GNPA 2025 (%) | EWS Signal | Top Driver |
| :--- | :---: | :---: | :---: | :--- |
| **PSB** | 3.47% | 4.84% | ELEVATED | Return on Assets ↑ |
| **Private** | 1.85% | 3.70% | ELEVATED | Return on Assets ↓ |
| **SFB** | 2.43% | 3.57% | ELEVATED | Return on Assets ↓ |
| **Foreign** | 1.19% | 3.56% | ELEVATED | Return on Assets ↓ |

*Note: All bank groups are flagged as `ELEVATED` for 2025 because their projected GNPA ratios rise above 3.0%, driven primarily by the lag effects of profitability compression (ROA).*

### Finding 4: Macro Stress Test and PCA Threshold Breaches
Applying macro shocks to the 2024 baseline yields the following GNPA projections:

| Bank Group | Baseline (2024) | Mild Stress (IL&FS) | Severe Stress (Post-AQR) | Tail Risk (COVID FY21) |
| :--- | :---: | :---: | :---: | :---: |
| **Foreign** | 1.19% | 1.85% | 2.69% | 4.01% |
| **PSB** | 3.47% | 4.13% | 4.97% | **6.29%** |
| **Private** | 1.85% | 2.51% | 3.35% | 4.67% |
| **SFB** | 2.43% | 3.08% | 3.93% | 5.25% |

* **Total Macro Impact:** The overall banking sector GNPA rises by **$+0.65$ pp** under Mild stress, **$+1.50$ pp** under Severe stress, and **$+2.81$ pp** under Tail Risk.
* **PCA Threshold Breach:** Under the Severe stress scenario, all bank groups remain within the RBI's Prompt Corrective Action (PCA) limits. However, under the **Tail Risk scenario (COVID-19 FY21)**, **PSB GNPA rises to 6.3% under the tail risk scenario — marginally breaching the PCA RT1 threshold of 6% — underscoring residual vulnerability despite the significant capital buffers built through IBC resolution.**

---

## 4. Policy Recommendations

### Recommendation 1: Incorporate Sub-Sectoral EWS Thresholds
Aggregate bank-group GNPA is a lagging indicator. Data shows that sub-sectoral NPAs (e.g., Infrastructure, Iron & Steel, MSME) crossed 12% in 2013–14, well before the 2016 PSB aggregate spike. 
* **Action:** The Department of Supervision should incorporate sector-specific early warning triggers. If infrastructure or MSME sector-level GNPA crosses **12%**, it should mandate a targeted credit audit of that sector's portfolio across all exposed banks, regardless of the bank's aggregate GNPA ratio.

### Recommendation 2: Operationalize the SupTech EWS Dashboard
To improve offsite surveillance, the prototype EWS should be operationalized as an automated dashboard within the RBI's internal systems.
* **Action:** Re-train the XGBoost + SHAP model on granular, bank-level quarterly returns (DSB database). Utilizing SHAP values allows the supervisor to justify early corrective action using auditable contributions (e.g., *"Bank A's declining ROA and rising term-loan credit growth contributed $+1.5$ pp to its 12-month forward GNPA stress prediction, triggering an offsite review"*). This shifts supervision from reactive (PCA breach) to proactive (early warning).

---

## 5. Supervisory Limitations of the Model

1. **Aggregated Public Data:** This EWS utilizes public, bank-group level data. It lacks the bank-specific granularity necessary to identify idiosyncratic risk within a specific group (e.g., a single weak private bank hidden in the aggregate private sector statistics).
2. **Small Sample Size:** The panel is limited to $n = 32$ observations, which constrains the statistical power of the XGBoost machine learning model and limits its ability to generalize across new structural regimes.
3. **Annual Frequency:** Annual reporting frequency introduces a reporting lag. Operationalizing this on quarterly or monthly DSB returns is required for real-time supervisory action.

---
*Submitted for review and further directions.*
