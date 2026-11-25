import sys
import os
sys.path.insert(0, os.path.abspath('src'))

import pandas as pd
import numpy as np
from sklearn.metrics import roc_auc_score, mean_absolute_error, mean_squared_error
from npa_ews.data import load_bank_level_panel, get_bank_level_model_ready, load_banking_panel, get_model_ready_frame
from npa_ews.models.dynamic_panel import DynamicPanelEstimator
from npa_ews.models.xgb_model import GnpaXGBModel, PcaBreachClassifier
from npa_ews import config

print('=== 1. SUMMARY STATISTICS OF BANK-LEVEL DATASET ===')
df_b = load_bank_level_panel()
clean_b = get_bank_level_model_ready(df_b)
vars_to_sum = ['gnpa_ratio', 'roa', 'credit_growth', 'cd_ratio', 'pcr', 'gdp_growth', 'repo_rate']
stats = clean_b[vars_to_sum].describe().T[['mean', 'std', 'min', '50%', 'max']]
print(stats.round(2))

print('\n=== 2. BANK GROUPS DISTRIBUTION ===')
print(clean_b['bank_group'].value_counts())

print('\n=== 3. ESTIMATION DETAILS FOR TABLE I ===')
est = DynamicPanelEstimator()
dyn_res = est.fit(clean_b)
print('Dynamic Model Params, T-stats, P-values:')
for k, v in dyn_res.params.items():
    print(f"{k}: coef={v:.3f}, t={dyn_res.tstats[k]:.2f}, p={dyn_res.pvalues[k]:.4f}")

stat_res = est.fit_static(clean_b)
print('\nStatic Model Params, T-stats, P-values:')
for k, v in stat_res.params.items():
    print(f"{k}: coef={v:.3f}, t={stat_res.tstats[k]:.2f}, p={stat_res.pvalues[k]:.4f}")

print('\n=== 4. BOOTSTRAP CONFIDENCE INTERVALS ON TEST SET ===')
train = clean_b[clean_b['year'] <= 2021]
test = clean_b[clean_b['year'] >= 2022]
feats = config.BANK_LEVEL_FEATURES

clf = PcaBreachClassifier(features=feats, target='pca_breach_next1yr').fit(train)
test_probs = clf.predict_proba(test)
y_true = test['pca_breach_next1yr'].astype(int).to_numpy()
base_auc = roc_auc_score(y_true, test_probs)

np.random.seed(42)
boot_aucs = []
for _ in range(1000):
    idx = np.random.choice(len(y_true), size=len(y_true), replace=True)
    if len(np.unique(y_true[idx])) > 1:
        boot_aucs.append(roc_auc_score(y_true[idx], test_probs[idx]))

ci_low, ci_high = np.percentile(boot_aucs, [2.5, 97.5])
print(f"XGBoost Test ROC-AUC: {base_auc:.3f} (95% CI: [{ci_low:.3f}, {ci_high:.3f}])")

print('\n=== 5. GLOBAL SHAP IMPORTANCES ===')
global_shap = clf.global_importance(clean_b)
print(global_shap)
