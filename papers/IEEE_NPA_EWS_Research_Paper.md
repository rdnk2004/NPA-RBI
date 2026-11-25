# Early Warning System for Non-Performing Assets in Indian Commercial Banks: An Explainable Machine Learning and Dynamic Econometric Approach

**Author details withheld for double-blind peer review**  
*Code and data repository link withheld for double-blind review*  

---

### Abstract
Non-Performing Assets (NPAs) pose chronic systemic vulnerabilities to financial stability and monetary transmission in emerging market banking systems. Following the 2015 Asset Quality Review (AQR) by the Reserve Bank of India (RBI), the Indian scheduled commercial banking sector experienced an acute bad-loan accumulation phase, peaking at a Gross NPA (GNPA) ratio of 11.2% in March 2018. Traditional regulatory surveillance often relies on static linear accounting ratios that omit autoregressive inertia, while modern machine learning models are frequently published without rigorous benchmarking against naive persistence baselines. In this study, we present a transparent, validation-disciplined Early Warning System (EWS) evaluated across a two-tier RBI dataset: an unbalanced bank-level panel (1,842 raw records across 135 banks over FY2004–FY2025, narrowing to $N = 649$ model-ready bank-years across 87 entities over FY2013–FY2024) and a sector-aggregate panel restored across FY2013–FY2024 ($N = 40$ group-years, PSB $n = 12$). First, dynamic panel fixed effects ($\alpha = 0.519, p < 0.001$) and Anderson-Hsiao first-difference IV ($\alpha = 0.938, p = 0.003$) establish heavy persistence alongside the dominant leading effects of Return on Assets (ROA: $-1.780$ and $-0.993, p < 0.001$) and Provision Coverage Ratio (PCR: $-0.105$ and $-0.060, p < 0.05$), consistent with the "bad management" hypothesis. Second, under strict out-of-time validation (train $\le 2021, n = 493$; test $\ge 2022, n = 156$ with 22 breach events), a simple naive persistence baseline ($GNPA_t$) outperforms Pooled OLS, Fixed Effects, Random Forest, and XGBoost on both continuous MAE (1.74% vs. 2.48%–6.70%) and RMSE (3.41% vs. 3.84%–8.08%), as well as discrete classification for Prompt Corrective Action (PCA) Risk Threshold 1 breaches (GNPA $\ge 6.0\%$ proxy: naive ROC-AUC 0.916 vs. XGBoost 0.907, paired bootstrap $p = 0.424$). Third, when current $GNPA_t$ is withheld to isolate forward-looking operational and macro signals, XGBoost achieves a covariate-only ROC-AUC of 0.710 [95% CI: 0.576, 0.822] (vs. Logit 0.650, $p = 0.398$), and TreeSHAP identifies ROA (mean $|\text{SHAP}| = 1.125$ pp) and lagged credit growth (0.413 pp) as primary leading drivers. Finally, a linear fixed-effects stress test with 1,000-draw block bootstrap projects PSB GNPAs reaching 6.93% under a COVID-style tail shock (90% CI: [4.80%, 8.05%], 80.7% breach probability) while flagging Small Finance Banks ($n = 4$) as LOW CONFIDENCE, and a micro-simulation across 65 active 2024 banks shows mean CRAR absorption of 3.27–3.90 pp with zero breaches of the 9.0% minimum floor.

**Index Terms**—Non-Performing Assets (NPAs), Early Warning Systems, Dynamic Panel Econometrics, Anderson-Hsiao IV, XGBoost, TreeSHAP, Validation Discipline, Prompt Corrective Action, Macroprudential Stress Testing.

---

## I. INTRODUCTION

The solvency, asset quality, and systemic resilience of commercial banks constitute the foundation of economic expansion and monetary transmission in bank-dominated emerging economies [1], [3]. In India, commercial banks intermediate the vast majority of domestic savings and credit allocation. Between 2011 and 2018, the Indian Scheduled Commercial Banking (SCB) sector endured an acute bad-loan accumulation phase, culminating in a peak Gross Non-Performing Asset (GNPA) ratio of 11.2% in March 2018, sequestering over ₹10.36 lakh crore in impaired advances [1], [3].

The historical origins of this stress were rooted in aggressive debt syndication during the 2004–2008 expansion, when lenders underwrote high-volume loans to infrastructure and industrial projects without commensurate risk buffers [4], [15]. Following regulatory delays and macroeconomic slowdowns, banks utilized restructuring schemes (e.g., Corporate Debt Restructuring and 5:25 refinancing) to postpone loss recognition [1], [15]. In late 2015, the Reserve Bank of India (RBI) initiated its Asset Quality Review (AQR), mandating realistic classification of impaired advances [2], [15], resulting in 11 out of 21 Public Sector Banks (PSBs) entering the Prompt Corrective Action (PCA) framework [1], [2].

This history motivates the development of Supervisory Technology (SupTech) Early Warning Systems (EWS). However, empirical early warning modeling faces two well-documented pitfalls: (1) omitting dynamic state-dependence creates specification error, whereas dynamic fixed-effects OLS suffers from Nickell bias in short panels [5], [6]; and (2) as Beutel et al. [8] demonstrated across European crises, complex machine learning classifiers frequently fail to outperform parsimonious statistical baselines out-of-sample due to overfitting on limited distress episodes. Furthermore, black-box ensembles encounter supervisory skepticism without interpretable attribution [8], [14].

Rather than asserting algorithmic superiority where none exists, this study prioritizes validation discipline and structural transparency across a two-tier RBI dataset:
1. We assemble an unbalanced micro-panel of 87 model-ready banks ($N = 649$ bank-years over FY2013–FY2024, drawn from 1,842 raw rows across 135 entities over FY2004–FY2025) alongside a restored 4-group sector panel ($N = 40$ group-years, PSB $n = 12$).
2. We estimate Static Fixed Effects, Dynamic Fixed Effects ($\alpha = 0.519, p < 0.001$), and Anderson-Hsiao First-Difference IV ($\alpha = 0.938, p = 0.003$) [5], proving that Return on Assets (ROA) and Provision Coverage Ratio (PCR) are robust leading signals.
3. We conduct a strictly honest out-of-time benchmark (FY2022–FY2024, $n = 156$) showing that naive persistence outperforms both linear and tree-based models on continuous error and matches or exceeds full-information ML classifiers (ROC-AUC 0.916 vs. 0.907).
4. We isolate pure forward-looking operational/macro signals via covariate-only XGBoost (AUC 0.710) and TreeSHAP [13], [14].
5. We implement a block-bootstrap macro stress test (Table III) paired with bank-level CRAR capital depletion accounting.

---

## II. RELATED WORK & THEORETICAL FOUNDATIONS

### A. Theoretical Models of Bank Asset Quality and Credit Cycles
Berger and DeYoung [4] formulated four core hypotheses linking bank operational efficiency, capitalization, and asset quality: *bad luck*, *bad management*, *skimping*, and *moral hazard*. Under the *bad management* hypothesis, operational inefficiencies and deficient credit appraisal Granger-cause subsequent surges in problem loans. Under *moral hazard*, thinly capitalized institutions underwrite high-variance credit under implicit sovereign guarantees [1], [4]. Cross-country studies by Louzis et al. [10], Messai and Jouini [9], and Ari, Chen, and Ratnovski [7] corroborate that non-performing loans exhibit strong autoregressive persistence and recover slowly after systemic shocks, driven jointly by GDP slowdowns, interest rate tightening, and profitability erosion.

### B. The Indian Banking NPA Crisis: Institutional Drivers
Acharya [1] and Rajan [15] documented that impaired advances during the 2015–2018 cycle were heavily concentrated in Public Sector Banks, driven by infrastructure concentration, weak project diligence, and extended forbearance. Mishra et al. [11] confirmed high autoregressive persistence and macroeconomic cyclicality in Indian banking panels using dynamic estimators. To codify intervention triggers, the RBI issued its Revised Prompt Corrective Action (PCA) Framework [2], establishing mandatory thresholds on capital adequacy, leverage, and asset quality.

### C. Evolution and Validation Discipline in Supervisory EWS
Early warning frameworks span static probits [4], [9], dynamic panel estimators [5], [6], and regularized machine learning [12]. Crucially, Beutel, List, and von Schweinitz [8] evaluated early warning models across 15 European economies and showed that standard logit models frequently outperform or match machine learning out-of-sample because tree ensembles overfit noisy crisis thresholds. To make tree ensembles inspectable, Lundberg and Lee [13] unified Shapley Additive Explanations (SHAP) and Lundberg et al. [14] derived polynomial-time TreeSHAP, enabling exact additive attribution of non-linear predictions.

---

## III. DATA ARCHITECTURE & FORENSIC RECONCILIATION

Our empirical pipeline integrates two complementary datasets constructed directly from official RBI *Statistical Tables Relating to Banks in India* (F4 Gross NPAs, F5 Key Ratios, F7 NPA Movements) and the Database on Indian Economy (DBIE) [3]:

1. **Tier 1: Bank-Level Micro-Panel:** Raw extraction across FY2004–FY2025 captures **1,842 unbalanced bank-year records** spanning **135 distinct banks** (reflecting post-2016 Small Finance Bank licensing and the 2017–2020 PSB mergers, where pre-2017 SBI associates remain separate reporting entities). Requiring non-missing values for two-year lagged credit growth, Provision Coverage Ratio (which begins in RBI's F7 tables in FY2013), and the 1-year ahead target narrows the model-ready panel to **FY2013–FY2024**, comprising **$N = 649$ bank-years across 87 unique entities**: Private Sector Banks (233 obs, 23 banks), Public Sector Banks (218 obs, 26 banks), Foreign Banks (167 obs, 29 banks), and Small Finance Banks (31 obs, 10 banks; IDBI Bank transitions from PSB to Private in FY2019 per RBI classification).
2. **Tier 2: Restored Macro Bank-Group Panel:** To conduct group-level macro stress testing without reporting breaks, aggregate annual totals from FY2004–FY2025 (74 group-years) restore the pre-2018 PSB series by summing "State Bank of India & Associates" and "Nationalised Banks" prior to RBI's 2018 unified "Public Sector Banks" category. After covariate and target alignment over FY2013–FY2024, this Tier 2 panel provides **$N = 40$ model-ready observations**: PSB ($n = 12$), Private ($n = 12$), Foreign ($n = 12$), and SFB ($n = 4$, licensed from 2016 onward and therefore flagged `LOW CONFIDENCE` under our $n < 8$ reliability rule).

---

## IV. SYSTEM METHODOLOGY & MATHEMATICAL FORMULATION

### A. Static, Dynamic Fixed Effects, and Anderson-Hsiao FD-IV Models
Under a static fixed-effects panel model, asset quality is formulated as:
$$GNPA_{i,t} = \alpha_0 + X_{i,t}^\top \beta + \mu_i + \varepsilon_{i,t} \tag{1}$$
where $\mu_i$ denotes time-invariant bank fixed effects. Incorporating one-year autoregressive persistence yields the Dynamic Fixed Effects (LSDV) specification:
$$GNPA_{i,t} = \alpha GNPA_{i,t-1} + X_{i,t}^\top \beta + \mu_i + \varepsilon_{i,t} \tag{2}$$

Because LSDV suffers from downward Nickell bias in short panels [5], we also estimate the Anderson-Hsiao First-Difference Instrumental Variable (FD-IV) estimator via 2SLS on consecutive-year differences:
$$\Delta GNPA_{i,t} = \alpha \Delta GNPA_{i,t-1} + \Delta X_{i,t}^\top \beta + \Delta \varepsilon_{i,t} \tag{3}$$
using the twice-lagged level $GNPA_{i,t-2}$ as an excluded instrument satisfying:
$$\mathbb{E}[ GNPA_{i,t-2} \cdot \Delta \varepsilon_{i,t} ] = 0 \tag{4}$$

### B. Machine Learning Classification & Regularization (XGBoost)
Under RBI Circular `RBI/2021-22/118` [2], the statutory PCA Risk Threshold 1 trigger is Net NPA $\ge 6.0\%$. Because offsite gross asset monitoring precedes provisioning offsets, we construct a binary gross-NPA distress proxy target ($GNPA \ge 6.0\%$ proxy):
$$Y_{i,t+1}^{\text{PCA}} = \mathbb{I}( GNPA_{i,t+1} \ge 6.0\% ) \tag{5}$$

We deploy Extreme Gradient Boosting (XGBoost) [12], minimizing a regularized empirical loss over $M$ additive trees:
$$\mathcal{L}^{(m)} = \sum_{k=1}^K l\left( y_k, \; \hat{y}_k^{(m-1)} + f_m(x_k) \right) + \Omega(f_m) \tag{6}$$
$$\Omega(f_m) = \gamma T_m + \frac{1}{2} \lambda \sum_{j=1}^{T_m} w_j^2 + \alpha_{\text{reg}} \sum_{j=1}^{T_m} |w_j| \tag{7}$$

To prevent apples-to-oranges benchmarking, we evaluate both **Regime A** (operational/macro covariates excluding $GNPA_t$, matching our Shapley driver model) and **Regime B** (full information including $GNPA_t$) against Naive Persistence ($GNPA_t \ge 6.0\%$).

### C. Game-Theoretic Explainability via TreeSHAP
To make non-linear tree classifications auditable [13], [14], TreeSHAP assigns exact additive attributions $\phi_j$ satisfying local efficiency:
$$\phi_j(f, x) = \sum_{S \subseteq F \setminus \{j\}} \frac{|S|!(|F| - |S| - 1)!}{|F|!} [ f(S \cup \{j\}) - f(S) ] \tag{8}$$
$$f(x) = \phi_0(f) + \sum_{j=1}^{|F|} \phi_j(f, x) \tag{9}$$

### D. Fixed-Effects Stress Test, Block Bootstrap & Capital Depletion
Using the restored Tier 2 bank-group Fixed Effects model ($\hat{\beta}_{\text{FE}}$), scenario shocks $\Delta X^{\text{shock}}$ map directly to projected group GNPAs from FY2024 baselines:
$$GNPA_g^{\text{stressed}} = \max\left( 0, \; GNPA_{g,2024} + \Delta X^{\text{shock}} \hat{\beta}_{\text{FE}} \right) \tag{10}$$

Sampling uncertainty is quantified via a 1,000-draw within-group block bootstrap resampling annual observations per cohort and refitting $\hat{\beta}_{\text{FE}}$. To link aggregate stress to micro-solvency across individual banks active in FY2024 ($n = 65$ with complete CRAR and GNPA), we compute incremental provisioning and post-shock Capital to Risk-Weighted Assets Ratios (CRAR) assuming standard Basel risk-density approximation $RWA_i \approx 0.70 \times A_{i,2024}$:
$$\Delta \text{Prov}_i = \left(\frac{\Delta GNPA^{\text{shock}}}{100}\right) \times A_{i,2024} \times PCR_{i,2024} \tag{11}$$
$$CRAR_i^{\text{post}} = \max\left( 0, \; CRAR_i^{\text{pre}} - \left[\frac{\Delta \text{Prov}_i}{0.70 \times A_{i,2024}}\right] \times 100 \right) \tag{12}$$

---

## V. EMPIRICAL RESULTS & DISCUSSION

### A. Econometric Estimation Findings
Table I reports all three panel estimators on Tier 1 data. Lagged GNPA exhibits significant persistence under Dynamic FE ($\alpha = 0.519, p < 0.001$) and rises to $\alpha = 0.938$ ($p = 0.003$) under Anderson-Hsiao FD-IV once downward Nickell bias is corrected [5]. Crucially, across all three specifications, higher Return on Assets significantly lowers future NPAs ($-2.564$, $-1.780$, and $-0.993$; all $p < 0.001$), and higher Provision Coverage Ratios significantly dampen subsequent GNPA ($-0.105, p = 0.045$ in Dynamic FE; $-0.060, p = 0.002$ in FD-IV). This provides robust support for Berger and DeYoung's [4] "bad management" mechanism.

#### TABLE I: Bank-Level Econometric Estimators (Tier 1 Micro-Panel)
| Variable | Static FE | Dynamic FE (LSDV) | Anderson-Hsiao FD-IV |
| :--- | :--- | :--- | :--- |
| **Lagged GNPA ($\alpha$)** | — | 0.519*** (0.070) | 0.938*** (0.313) |
| **Return on Assets (ROA)** | -2.564*** (0.396) | -1.780*** (0.350) | -0.993*** (0.269) |
| **Credit Growth (t-2)** | -0.019** (0.009) | 0.011 (0.009) | 0.021 (0.014) |
| **Credit-Deposit Ratio** | -0.004*** (0.000) | -0.062 (0.061) | -0.002 (0.018) |
| **Provision Coverage (PCR)** | -0.051 (0.038) | -0.105** (0.052) | -0.060*** (0.020) |
| **GDP Growth (%)** | 0.071 (0.064) | 0.112* (0.068) | 0.035 (0.036) |
| **Policy Repo Rate (%)** | -0.949*** (0.341) | -0.517* (0.300) | -0.375* (0.226) |

*\* $p < 0.10$, \*\* $p < 0.05$, \*\*\* $p < 0.01$. Entity-clustered standard errors in parentheses. Static FE: $N = 649$ (87 banks, Within $R^2 = 0.341$). Dynamic FE: $N = 562$ (83 banks, Within $R^2 = 0.443$). FD-IV2SLS (differenced, consecutive years): $N = 456$ (72 banks, $R^2 = -0.293$).*

### B. Out-of-Time Predictive Performance & Validation Discipline
Training exclusively up to FY2021 ($n = 493$) and testing out-of-time on FY2022–FY2024 ($n = 156$, containing 22 breach events: 18 continuing from $t$, 4 new onsets, and 21 recoveries) yields a sobering validation finding (Table II). First, on continuous level forecasting, Naive Persistence ($GNPA_t$) achieves $\text{MAE} = 1.74\%$, $\text{RMSE} = 3.41\%$, and $R^2 = 0.213$—beating every parametric and tree model on **both MAE and RMSE**, even when $GNPA_t$ is supplied in Regime B ($\text{XGBoost}+GNPA_t$: MAE 2.48%, RMSE 3.84%; $\text{Pooled OLS}+GNPA_t$: MAE 2.70%, RMSE 4.16%). Without $GNPA_t$ (Regime A), linear models extrapolate poorly (Pooled OLS MAE 6.42%, RMSE 7.78%; Panel FE MAE 6.70%, RMSE 8.08%).

Second, on discrete PCA-proxy breach classification (Table II), a naive persistence classifier (flagging $GNPA_t \ge 6.0\%$, ranked by $GNPA_t$) achieves $\text{ROC-AUC} = 0.916$ [95% CI: 0.829, 0.982], $\text{Accuracy} = 84.0\%$, $\text{Precision} = 46.2\%$, $\text{Recall} = 81.8\%$ (18/22), and $F_1 = 0.590$. Full-information $\text{XGBoost}+GNPA_t$ reaches $\text{ROC-AUC} = 0.907$ [0.813, 0.982] and $\text{Accuracy} = 82.1\%$—statistically indistinguishable from naive persistence (paired bootstrap $p = 0.424$). Only when $GNPA_t$ is intentionally withheld (Regime A) to isolate forward operational/macro risk signals does XGBoost achieve non-trivial ranking power ($\text{ROC-AUC} = 0.710$ [0.576, 0.822], $\text{Accuracy} = 76.3\%$), though its advantage over Logit (0.650) is not statistically significant ($p = 0.398$). This directly confirms Beutel et al.'s [8] caution against overclaiming ML gains over parsimonious persistence rules.

#### TABLE II: Out-of-Time Test Benchmarks (FY2022–FY2024, N = 156, 22 Breaches)
| Model (Feature Set) | MAE | RMSE | ROC-AUC [95% CI] | Accuracy | Recall |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Naive Persistence ($GNPA_t$)** | **1.74%** | **3.41%** | **0.916** [0.829, 0.982] | **84.0%** | 81.8% |
| **Reg. A (No $GNPA_t$): Logit/OLS** | 6.42% | 7.78% | 0.650 [0.471, 0.808] | 63.5% | 68.2% |
| **Reg. A (No $GNPA_t$): Random Forest** | 3.15% | 4.49% | 0.692 [0.547, 0.809] | 71.2% | 54.5% |
| **Reg. A (No $GNPA_t$): XGBoost** | 3.22% | 4.45% | 0.710 [0.576, 0.822] | 76.3% | 50.0% |
| **Reg. B (+$GNPA_t$): Logit/OLS** | 2.70% | 4.16% | 0.872 [0.760, 0.959] | 76.9% | 81.8% |
| **Reg. B (+$GNPA_t$): Random Forest** | 2.96% | 4.12% | 0.868 [0.750, 0.960] | 80.8% | **86.4%** |
| **Reg. B (+$GNPA_t$): XGBoost** | 2.48% | 3.84% | 0.907 [0.813, 0.982] | 82.1% | 81.8% |

*All models evaluated on identical $N = 156$ test observations (22 breaches). Reg. A OLS row pairs Pooled OLS regression (MAE/RMSE) with Logistic Regression classification. Paired bootstrap $p$-values: Reg. A XGBoost vs. Logit $p = 0.398$; Naive vs. Reg. B XGBoost $p = 0.424$. Panel FE (Reg. A) gives MAE 6.70%, RMSE 8.08%.*

### C. TreeSHAP Game-Theoretic Attribution
On the Regime A covariate-only classifier, global TreeSHAP feature importances [13], [14] confirm that forward distress is primarily explained by Return on Assets (mean $|\text{SHAP}| = 1.125$ pp), followed by two-year lagged credit growth (0.413 pp), GDP growth (0.404 pp), Provision Coverage Ratio (0.316 pp), Credit-Deposit ratio (0.254 pp), policy repo rate (0.075 pp), and CPI inflation (0.032 pp). By comparison, on the aggregate 4-group panel ($n = 40$), ROA also ranks first at 0.546 pp. Both micro and macro evidence independently establish profitability compression as the earliest measurable precursor of asset impairment.

### D. Macroeconomic Stress Testing & Bank Capital Depletion
Table III reports the Tier 2 Fixed Effects stress projections ($\text{Within } R^2 = 0.665, N = 40$; ROA $\text{coef} = -3.414$) calibrated to historical RBI stress shocks. Under the COVID-FY21 Tail Risk scenario (GDP $-3.0$ pp, repo $+200$ bps, credit growth $-6.0$ pp, ROA $-0.8$ pp; composite $+3.46$ pp GNPA impact), PSB point-estimate GNPA rises from 3.47% to 6.93% (bootstrap mean 6.68%, 90% CI: [4.80%, 8.05%], 80.7% breach probability). Crucially, restoring pre-2018 PSB history yields $n = 12$ reliable observations for PSBs, Private, and Foreign banks, leaving only Small Finance Banks ($n = 4$, tail risk 5.89%, 90% CI: [3.76%, 7.01%]) flagged as `LOW CONFIDENCE`.

Translating the $+3.46$ pp Tail Risk GNPA shock to individual FY2024 balance sheets across all 65 active banks with complete CRAR data (12 PSBs, 21 Private, 20 Foreign, 12 SFBs) via Eqs. (11)–(12) indicates mean CRAR absorption of 3.90 pp for PSBs (16.42% to 12.52%), 3.49 pp for Private banks (18.20% to 14.71%), 3.60 pp for Foreign banks (34.63% to 31.03%), and 3.27 pp for SFBs (23.41% to 20.14%), with zero banks breaching the 9.0% statutory CRAR minimum due to strengthened post-2021 capital buffers.

#### TABLE III: Restored Group Stress Projections & Tail Uncertainty (Tier 2, N = 40)
| Group | Baseline '24 | Severe (AQR) | Tail Risk (COVID) | 90% Bootstrap CI (Breach Prob) | Confidence |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Foreign** | 1.19% | 3.24% | 4.65% | [2.52%, 5.77%] (2.9%) | reliable ($n=12$) |
| **Private** | 1.85% | 3.90% | 5.31% | [3.18%, 6.43%] (12.5%) | reliable ($n=12$) |
| **PSB** | 3.47% | 5.52% | 6.93% | [4.80%, 8.05%] (80.7%) | reliable ($n=12$) |
| **SFB** | 2.43% | 4.48% | 5.89% | [3.76%, 7.01%] (38.7%) | LOW ($n=4$) |

*Point estimates from `run_stress_test` on restored `banking_panel.csv` ($N=40$); 90% CIs and PCA breach probabilities ($>6.0\%$) from 1,000 block-bootstrap draws. Groups with $n < 8$ flagged LOW CONFIDENCE.*

---

## VI. LIMITATIONS & POLICY IMPLICATIONS

Three methodological limitations govern interpretation: (1) The out-of-time test partition contains 156 bank-years with 22 breach events (only 4 new onsets), yielding wide confidence intervals and favoring simple persistence; (2) Our classification target uses $GNPA \ge 6.0\%$ as a gross proxy for the statutory Net-NPA PCA trigger [2]; and (3) Group-level stress elasticities rest on $N = 40$ observations, where SFBs ($n = 4$) carry substantial small-sample uncertainty.

For supervisory policy, our results support three disciplined practices: (1) **Mandatory Naive Benchmarking:** SupTech classifiers should never be deployed without demonstrating superiority over persistence ($GNPA_t$) out-of-sample; (2) **Profitability-Led Surveillance:** Because ROA dominates both dynamic panel regressions and TreeSHAP rankings, offsite monitoring should flag profitability erosion 12–24 months ahead of asset deterioration; and (3) **Uncertainty-Aware Stress Testing:** Scenario projections must publish bootstrap intervals and explicit sample-size flags.

---

## VII. CONCLUSION

This study presented a reproducible, validation-disciplined Early Warning System for Indian commercial banks built across a two-tier RBI dataset ($N = 649$ bank-level observations across 87 entities and $N = 40$ restored bank-group observations). Dynamic Fixed Effects ($\alpha = 0.519$) and Anderson-Hsiao FD-IV ($\alpha = 0.938$) confirm heavy credit inertia alongside the leading causal roles of ROA and PCR. Crucially, honest out-of-time testing shows that naive persistence outperforms both linear and machine learning models on continuous error (MAE 1.74%, RMSE 3.41%) and matches full-information XGBoost on PCA breach detection (AUC 0.916 vs. 0.907, $p = 0.424$). Consequently, the core regulatory value of explainable ML and dynamic econometrics lies in forward driver identification (TreeSHAP ROA = 1.125 pp) and uncertainty-quantified macro stress testing.

---

## REFERENCES

[1] V. V. Acharya, *Quest for Restoring Financial Stability in India*. New Delhi, India: SAGE Publications, 2020.  
[2] Reserve Bank of India, "Prompt Corrective Action (PCA) framework for scheduled commercial banks," RBI Circular RBI/2021-22/118, DOS.CO.PPG.SEC.No.4/11.01.005/2021-22, Nov. 2, 2021.  
[3] Reserve Bank of India, *Report on Trend and Progress of Banking in India 2023-24*, Reserve Bank of India, Mumbai, India, Dec. 2024.  
[4] A. N. Berger and R. DeYoung, "Problem loans and cost efficiency in commercial banks," *Journal of Banking & Finance*, vol. 21, no. 6, pp. 849–870, Jun. 1997.  
[5] M. Arellano and S. Bond, "Some tests of specification for panel data: Monte Carlo evidence and an application to employment equations," *The Review of Economic Studies*, vol. 58, no. 2, pp. 277–297, Apr. 1991.  
[6] R. Blundell and S. Bond, "Initial conditions and moment restrictions in dynamic panel data models," *Journal of Econometrics*, vol. 87, no. 1, pp. 115–143, Aug. 1998.  
[7] A. Ari, S. Chen, and L. Ratnovski, "The dynamics of non-performing loans during banking crises: A new database," *European Central Bank Working Paper Series*, no. 2395, Apr. 2020.  
[8] J. Beutel, S. List, and G. von Schweinitz, "Does machine learning help us predict banking crises?," *Journal of Financial Stability*, vol. 45, Art. no. 100693, Dec. 2019, doi: 10.1016/j.jfs.2019.100693.  
[9] A. S. Messai and F. Jouini, "Micro and macro determinants of non-performing loans," *International Journal of Economics and Financial Issues*, vol. 3, no. 4, pp. 852–860, 2013.  
[10] D. P. Louzis, A. T. Vouldis, and V. L. Metaxas, "Macroeconomic and bank-specific determinants of non-performing loans in Greece: A comparative study of mortgage, business and consumer loan portfolios," *Journal of Banking & Finance*, vol. 36, no. 4, pp. 1012–1027, Apr. 2012.  
[11] A. K. Mishra, S. Jain, and M. Abid, "Non-performing assets and its determinants in the Indian banking system: An empirical analysis using dynamic panel data models," *International Journal of Finance & Economics*, vol. 26, no. 4, pp. 5948–5962, Oct. 2021.  
[12] T. Chen and C. Guestrin, "XGBoost: A scalable tree boosting system," in *Proc. 22nd ACM SIGKDD Int. Conf. Knowledge Discovery and Data Mining (KDD '16)*, San Francisco, CA, USA, 2016, pp. 785–794.  
[13] S. M. Lundberg and S.-I. Lee, "A unified approach to interpreting model predictions," in *Advances in Neural Information Processing Systems (NeurIPS 2017)*, Long Beach, CA, USA, 2017, pp. 4765–4774.  
[14] S. M. Lundberg, G. Erion, H. Chen, A. DeGrave, J. M. Prutkin, B. Nair, R. Katz, and S.-I. Lee, "From local explanations to global understanding with explainable AI for trees," *Nature Machine Intelligence*, vol. 2, no. 1, pp. 56–67, Jan. 2020.  
[15] R. G. Rajan, "Note to the Parliamentary Estimates Committee on Bank NPAs," Parliament of India, New Delhi, India, Sep. 2018.  
