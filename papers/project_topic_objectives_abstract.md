# Project Topic, Objectives, and IEEE Draft Abstract

**Project Title (Recommended for IEEE):**  
# Early Warning System for Non-Performing Assets in Indian Commercial Banks: An Explainable Machine Learning and Dynamic Econometric Approach

**Alternative Title Options:**
1. *A Hybrid Dynamic Econometric and Explainable AI Framework for Banking Distress Surveillance in India*
2. *Supervisory Early Warning System for Indian Scheduled Commercial Banks using XGBoost and TreeSHAP*
3. *Predicting Asset Quality Distress and Capital Adequacy Breaches in Indian Banking: An Explainable Machine Learning Approach*

---

## 1. Problem Statement & Research Context

Non-Performing Assets (NPAs) pose severe systemic risks to financial stability, particularly in bank-dominated emerging economies like India. Between 2015 and 2018, the Indian commercial banking sector experienced a systemic asset quality crisis, where Gross NPAs surged to a peak of 11.2% (exceeding INR 10 lakh crore), forcing 11 Public Sector Banks into the Reserve Bank of India’s (RBI) Prompt Corrective Action (PCA) framework. 

Existing supervisory monitoring frameworks and empirical research suffer from three critical deficiencies:
1. **The Reporting Break Blind Spot:** Post-merger studies often suffer from an artificial 14-year data truncation bug, missing pre-2018 Public Sector Bank data due to the historical amalgamation of State Bank of India with its associate banks.
2. **The Supervisory Forecasting Dilemma:** Classical linear econometric models offer structural causal interpretability but fail to capture non-linear tipping points. Conversely, complex machine learning models struggle to beat simple persistence in predicting continuous macro point drifts and are rejected by regulators as opaque "black boxes."
3. **Absence of Discrete Regulatory Threshold Early Warning:** Traditional early warning systems attempt to forecast continuous default numbers rather than classifying the actionable, non-linear regulatory danger triggers (such as RBI PCA Threshold breaches at $GNPA \ge 6.0\%$).

---

## 2. Project Objectives

### Primary Objective:
To design, implement, and validate an integrated **Dual-Engine Supervisory Early Warning System (SupTech)** combining dynamic panel econometrics and explainable machine learning to detect systemic bank asset quality deterioration and regulatory capital impairment 12 to 24 months in advance.

### Specific Technical Objectives:
1. **Forensic Data Reconstruction:**
   - Resolve historical RBI reporting break ruptures across the 2017 SBI consolidation, restoring an uninterrupted 21-year macro time series (2004–2025).
   - Synthesize a comprehensive micro-longitudinal panel of **649 model-ready bank-year observations spanning 87 Scheduled Commercial Banks** (Public, Private, Foreign, and Small Finance Banks) across 2013–2024.
2. **Dynamic Econometric Modeling:**
   - Formulate a Dynamic Panel First-Difference Instrumental Variable (IV) model to resolve Nickell (1981) dynamic endogeneity bias.
   - Quantify structural asset quality persistence ($\alpha$) and empirically resolve the "Credit Boom Inversion" paradox, proving the 2-year lagged transmission of credit expansion to bad loans.
3. **Machine Learning Early Warning Classifier:**
   - Engineer gradient-boosted decision tree ensembles (XGBoost) and Random Forests to predict discrete statutory distress events: **RBI Prompt Corrective Action (PCA) Threshold 1 Breaches ($GNPA \ge 6.0\%$)**.
   - Validate performance using a strict out-of-time walk-forward protocol (Train $\le 2021$, Test $\ge 2022$) to guarantee zero temporal data leakage.
4. **Explainable AI (XAI) Supervisory Interpretation:**
   - Deploy TreeSHAP (Shapley Additive Explanations) based on cooperative game theory to provide mathematically guaranteed local and global feature attributions.
   - Map non-linear supervisory tipping points, such as the **"Profitability Cliff"** (RoA $< 0.50\%$) and Credit-to-Deposit leverage compounding.
5. **Bounded Macro-Stress Testing & Capital Depletion Simulation:**
   - Implement a logit-transformed satellite projection model ensuring stressed default ratios remain strictly bounded within $(0, 100\%)$.
   - Simulate bank-by-bank Basel III regulatory capital depletion, computing post-shock Capital to Risk-Weighted Assets Ratios (CRAR) and identifying institutions breaching the statutory 9.0% minimum capital floor under severe macroeconomic stress scenarios.

---

## 3. IEEE Draft Abstract

```
========================================================================================
                                   IEEE DRAFT ABSTRACT
========================================================================================
```

**Title:** Early Warning System for Non-Performing Assets in Indian Commercial Banks: An Explainable Machine Learning and Dynamic Econometric Approach

**Abstract:**  
Accurate early detection of bank asset quality distress is essential for macroprudential regulation and systemic financial stability. However, supervisory surveillance faces an operational dilemma: classical linear econometric models provide structural macroeconomic interpretability but fail to capture non-linear default tipping points, while machine learning models often operate as uninterpretable black boxes and fail to outperform naive persistence in continuous forecasting. 

This paper develops an integrated dual-engine Supervisory Technology (SupTech) early warning architecture evaluated on the Indian Scheduled Commercial Banking sector. First, resolving historical statistical ruptures caused by public sector bank amalgamations, we reconstruct an uninterrupted 21-year macro panel and synthesize an extensive micro-longitudinal dataset of 649 bank-year observations spanning 87 commercial banks over 2013–2024. Second, dynamic panel econometric estimation resolves Nickell endogeneity bias, establishing significant asset quality persistence ($\alpha = 0.5457, t = 9.13, p < 0.001$) and confirming that credit expansion increases default formation with a two-year lag ($\beta = +0.0393, p = 0.013$). Third, under strict out-of-time walk-forward validation (Train $\le 2021$, Test $\ge 2022$), we demonstrate that while persistence dominates continuous point forecasting, an Extreme Gradient Boosting (XGBoost) classifier decisively outperforms classical logistic regression in predicting statutory Reserve Bank of India Prompt Corrective Action (PCA) Threshold 1 breaches ($GNPA \ge 6.0\%$), achieving an ROC-AUC of 0.710 versus 0.650 and an accuracy of 76.3% versus 63.5%. 

Using TreeSHAP explainability, we identify non-linear supervisory thresholds, revealing an exponential default risk surge when bank Return on Assets drops below 0.50% under elevated credit-deposit leverage. Finally, we formulate a logit-bounded satellite stress-testing module integrated with a micro-prudential capital adequacy simulation, projecting post-shock Capital to Risk-Weighted Assets Ratios (CRAR) under adverse macro scenarios. This architecture provides central banks and commercial lenders with an empirical, transparent, and policy-actionable early warning platform.

**Index Terms / Keywords:**  
Early Warning Systems, Non-Performing Assets, Indian Banking, Dynamic Panel Econometrics, Explainable AI, XGBoost, TreeSHAP, Prompt Corrective Action, Macroprudential Stress Testing, Capital Adequacy (CRAR).

---

## 4. Summary Table of Key Results (For Reviewers & Presentation)

| Dimension | Classical / Baseline Approach | Our Upgraded Framework | Empirical Advantage |
| :--- | :--- | :--- | :--- |
| **Data Scope** | 32 aggregated macro rows (truncated post-2018) | **649 bank-years across 87 individual banks** (2013–2024) | Eliminates aggregation bias; restores 14 years of public bank history. |
| **Credit Boom Impact** | $-0.028$ (spurious negative sign due to truncation) | **$+0.0393$ ($p = 0.013$, 2-year lag)** | Restores theoretical Minskyan credit cycle dynamics. |
| **Asset Quality Persistence** | Ignored in static regressions | **$\alpha = 0.5457$ ($t = 9.13, p < 0.001$)** | Corrects Nickell (1981) dynamic panel bias. |
| **PCA Breach Accuracy** | 63.5% (Logistic Regression) | **76.3% (XGBoost Ensemble)** | **+12.8 percentage points** improvement in out-of-time accuracy. |
| **PCA Breach ROC-AUC** | 0.650 (Logit) | **0.710 (XGBoost Classifier)** | Superior discrimination of regulatory distress tipping points. |
| **Model Interpretability** | Uninterpretable black box in standard ML | **TreeSHAP Game-Theoretic Attribution** | Discovers the $0.50\%$ RoA "Profitability Cliff" and CD risk compounding. |
| **Stress Testing Engine** | Linear OLS (unbounded, can yield $< 0\%$ or $> 100\%$) | **Logit-Linked Satellite Model + CRAR Depletion** | Bounded in $(0, 100\%)$; projects 14/87 banks breaching 9.0% min. capital. |

---

## 5. Ready-to-Print Handout for Your Guide / Ma'am

* **File Location on Disk:** `d:\AI-ML Projects\NPA\papers\project_topic_objectives_abstract.md`
* **Full Academic Paper:** `d:\AI-ML Projects\NPA\papers\npa_ews_research_paper.md`
* **Codebase & API Status:** Branch `research-upgrade` (81/81 automated tests passing).
