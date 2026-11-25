import sys, os
sys.path.insert(0, os.path.abspath('src'))

import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.metrics import (
    mean_absolute_error, mean_squared_error, r2_score,
    roc_auc_score, accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix
)
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier, XGBRegressor

from npa_ews import config
from npa_ews.data import load_bank_level_panel, get_bank_level_model_ready

df_b = load_bank_level_panel()
clean_b = get_bank_level_model_ready(df_b, features=config.BANK_LEVEL_FEATURES, target="gnpa_next1yr")
clean_b = clean_b.dropna(subset=["pca_breach_next1yr"]).copy()

train = clean_b[clean_b["year"] <= 2021].copy()
test = clean_b[clean_b["year"] >= 2022].copy()
y_test_reg = test["gnpa_next1yr"].to_numpy()
y_test_cls = test["pca_breach_next1yr"].astype(int).to_numpy()

# Check onset vs persistent breaches in test set
test_curr_breach = (test["gnpa_ratio"] >= 6.0).astype(int).to_numpy()
print(f"Test set (n={len(test)}): total breaches next1yr = {y_test_cls.sum()}")
print(f"  Already >=6% in t: {( (test_curr_breach==1) & (y_test_cls==1) ).sum()}")
print(f"  New onset (<6% in t -> >=6% in t+1): {( (test_curr_breach==0) & (y_test_cls==1) ).sum()}")
print(f"  Recovered (>=6% in t -> <6% in t+1): {( (test_curr_breach==1) & (y_test_cls==0) ).sum()}")

# Test Regime B: adding gnpa_ratio to BANK_LEVEL_FEATURES
feats_full = ["gnpa_ratio"] + config.BANK_LEVEL_FEATURES

print("\n=== REGIME B: REGRESSION WITH GNPA_t INCLUDED (n_test = 156) ===")
X_tr_f = sm.add_constant(train[feats_full])
X_te_f = sm.add_constant(test[feats_full], has_constant="add")
ols_f = sm.OLS(train["gnpa_next1yr"], X_tr_f).fit().predict(X_te_f[X_tr_f.columns]).to_numpy()
rf_f = RandomForestRegressor(n_estimators=100, max_depth=4, random_state=42).fit(train[feats_full], train["gnpa_next1yr"]).predict(test[feats_full])
xgb_f = XGBRegressor(n_estimators=100, max_depth=3, learning_rate=0.05, subsample=0.8, random_state=42).fit(train[feats_full], train["gnpa_next1yr"]).predict(test[feats_full])
naive_reg = test["gnpa_ratio"].to_numpy()

for name, p in [("Naive (GNPA_t)", naive_reg), ("Pooled OLS + GNPA_t", ols_f), ("Random Forest + GNPA_t", rf_f), ("XGBoost + GNPA_t", xgb_f)]:
    print(f"  {name:24s}: MAE={mean_absolute_error(y_test_reg, p):.3f}, RMSE={np.sqrt(mean_squared_error(y_test_reg, p)):.3f}, R2={r2_score(y_test_reg, p):.3f}")

print("\n=== REGIME B: CLASSIFICATION WITH GNPA_t INCLUDED (n_test = 156, pos=22) ===")
logit_f = LogisticRegression(max_iter=1000, random_state=42).fit(train[feats_full], train["pca_breach_next1yr"].astype(int))
logit_fp = logit_f.predict_proba(test[feats_full])[:, 1]
rf_cf = RandomForestClassifier(n_estimators=100, max_depth=4, random_state=42).fit(train[feats_full], train["pca_breach_next1yr"].astype(int))
rf_cfp = rf_cf.predict_proba(test[feats_full])[:, 1]
xgb_cf = XGBClassifier(n_estimators=100, max_depth=3, learning_rate=0.05, subsample=0.8, eval_metric="logloss", random_state=42).fit(train[feats_full], train["pca_breach_next1yr"].astype(int))
xgb_cfp = xgb_cf.predict_proba(test[feats_full])[:, 1]

for name, prob, pred in [
    ("Naive (GNPA_t >= 6%)", test["gnpa_ratio"].to_numpy()/100.0, (test["gnpa_ratio"]>=6.0).astype(int).to_numpy()),
    ("Logit + GNPA_t", logit_fp, (logit_fp>=0.5).astype(int)),
    ("Random Forest + GNPA_t", rf_cfp, (rf_cfp>=0.5).astype(int)),
    ("XGBoost + GNPA_t", xgb_cfp, (xgb_cfp>=0.5).astype(int)),
]:
    auc = roc_auc_score(y_test_cls, prob)
    acc = accuracy_score(y_test_cls, pred)
    prec = precision_score(y_test_cls, pred, zero_division=0)
    rec = recall_score(y_test_cls, pred, zero_division=0)
    f1 = f1_score(y_test_cls, pred, zero_division=0)
    print(f"  {name:24s}: AUC={auc:.3f}, Acc={acc:.3f}, Prec={prec:.3f}, Rec={rec:.3f}, F1={f1:.3f}")
