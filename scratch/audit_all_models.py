import sys, os
sys.path.insert(0, os.path.abspath('src'))

import numpy as np
import pandas as pd
import statsmodels.api as sm
from linearmodels.panel import PanelOLS
from linearmodels.iv import IV2SLS
from sklearn.metrics import (
    mean_absolute_error, mean_squared_error, r2_score,
    roc_auc_score, accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix
)
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression

from npa_ews import config
from npa_ews.data import (
    load_banking_panel, get_model_ready_frame, group_reliability,
    load_bank_level_panel, get_bank_level_model_ready
)
from npa_ews.models.panel_fe import FixedEffectsRegressor
from npa_ews.models.xgb_model import GnpaXGBModel, PcaBreachClassifier
from npa_ews.stress import run_stress_test, bootstrap_stress_test, run_logit_stress_test, simulate_bank_capital_depletion

# 1. Check Bank-Level Panel (after understanding group labels)
df_b = load_bank_level_panel()
clean_b = get_bank_level_model_ready(df_b, features=config.BANK_LEVEL_FEATURES, target="gnpa_next1yr")
clean_b = clean_b.dropna(subset=["pca_breach_next1yr"]).copy()

print("=== BANK-LEVEL PANEL SUMMARY ===")
print(f"Raw: {len(df_b)} rows, {df_b['bank_clean'].nunique()} banks, {df_b['year'].min()}-{df_b['year'].max()}")
print(f"Model-ready: {len(clean_b)} rows, {clean_b['bank_clean'].nunique()} banks, {clean_b['year'].min()}-{clean_b['year'].max()}")

# 2. Check Pooled OLS & Naive Classifier on the SAME 156 bank-level test rows!
feats = config.BANK_LEVEL_FEATURES
train = clean_b[clean_b["year"] <= 2021].copy()
test = clean_b[clean_b["year"] >= 2022].copy()
print(f"\nSplit: train={len(train)} (<=2021), test={len(test)} (>=2022)")
y_test_reg = test["gnpa_next1yr"].to_numpy()
y_test_cls = test["pca_breach_next1yr"].astype(int).to_numpy()
print(f"Test positive breaches (GNPA_next1yr >= 6%): {y_test_cls.sum()} / {len(y_test_cls)} ({y_test_cls.mean()*100:.1f}%)")

# Regression models on bank-level test set
naive_reg = test["gnpa_ratio"].to_numpy()

X_tr = sm.add_constant(train[feats])
X_te = sm.add_constant(test[feats], has_constant="add")
ols = sm.OLS(train["gnpa_next1yr"], X_tr).fit()
ols_reg = ols.predict(X_te[X_tr.columns]).to_numpy()

# Entity FE Regression (fit on train banks present in test, fallback to group/overall mean if unseen)
tr_fe = train.set_index(["bank_clean", "year"])
fe_mod = PanelOLS(tr_fe["gnpa_next1yr"], tr_fe[feats], entity_effects=True).fit()
# Recover entity effects for prediction
ent_eff = fe_mod.estimated_effects.groupby(level=0).mean()["estimated_effects"]
mean_eff = ent_eff.mean()
test_eff = test["bank_clean"].map(ent_eff).fillna(mean_eff).to_numpy()
fe_reg = (test[feats].to_numpy() @ fe_mod.params.to_numpy()) + test_eff

rf_reg_mod = RandomForestRegressor(n_estimators=100, max_depth=5, random_state=config.RANDOM_SEED).fit(train[feats], train["gnpa_next1yr"])
rf_reg = rf_reg_mod.predict(test[feats])

xgb_reg_mod = GnpaXGBModel(features=feats, target="gnpa_next1yr").fit(train, test)
xgb_reg = xgb_reg_mod.predict(test)

print("\n=== TABLE II-A: BANK-LEVEL REGRESSION (n_test = 156) ===")
for name, preds in [
    ("Naive Persistence (GNPA_t)", naive_reg),
    ("Pooled OLS", ols_reg),
    ("Panel Fixed Effects", fe_reg),
    ("Random Forest", rf_reg),
    ("XGBoost", xgb_reg),
]:
    mae = mean_absolute_error(y_test_reg, preds)
    rmse = np.sqrt(mean_squared_error(y_test_reg, preds))
    r2 = r2_score(y_test_reg, preds)
    print(f"  {name:28s}: MAE={mae:.3f}, RMSE={rmse:.3f}, R2={r2:.3f}")

# Classification models on bank-level test set
naive_cls_pred = (test["gnpa_ratio"] >= 6.0).astype(int).to_numpy()
naive_cls_score = test["gnpa_ratio"].to_numpy() / 100.0  # monotone risk score for AUC

logit = LogisticRegression(max_iter=1000, random_state=config.RANDOM_SEED).fit(train[feats], train["pca_breach_next1yr"].astype(int))
logit_prob = logit.predict_proba(test[feats])[:, 1]
logit_pred = (logit_prob >= 0.5).astype(int)

rf_cls = RandomForestClassifier(n_estimators=100, max_depth=4, random_state=config.RANDOM_SEED).fit(train[feats], train["pca_breach_next1yr"].astype(int))
rf_prob = rf_cls.predict_proba(test[feats])[:, 1]
rf_pred = (rf_prob >= 0.5).astype(int)

xgb_cls = PcaBreachClassifier(features=feats, target="pca_breach_next1yr").fit(train)
xgb_prob = xgb_cls.predict_proba(test)
xgb_pred = (xgb_prob >= 0.5).astype(int)

print("\n=== TABLE II-B: BANK-LEVEL PCA PROXY CLASSIFICATION (n_test = 156, pos = 22) ===")
for name, prob, pred in [
    ("Naive Persistence (GNPA_t >= 6%)", naive_cls_score, naive_cls_pred),
    ("Logistic Regression", logit_prob, logit_pred),
    ("Random Forest Classifier", rf_prob, rf_pred),
    ("XGBoost Classifier", xgb_prob, xgb_pred),
]:
    auc = roc_auc_score(y_test_cls, prob)
    acc = accuracy_score(y_test_cls, pred)
    prec = precision_score(y_test_cls, pred, zero_division=0)
    rec = recall_score(y_test_cls, pred, zero_division=0)
    f1 = f1_score(y_test_cls, pred, zero_division=0)
    tn, fp, fn, tp = confusion_matrix(y_test_cls, pred).ravel()
    print(f"  {name:34s}: AUC={auc:.3f}, Acc={acc:.3f}, Prec={prec:.3f}, Rec={rec:.3f}, F1={f1:.3f} (TP={tp}, FP={fp}, FN={fn}, TN={tn})")

# 3. Check Anderson-Hsiao FD-IV2SLS on bank_level_panel
panel_df = clean_b.sort_values(["bank_clean", "year"]).copy()
# Check consecutive years before differencing!
panel_df["year_diff"] = panel_df.groupby("bank_clean")["year"].diff()
panel_df["gnpa_lag1"] = panel_df.groupby("bank_clean")["gnpa_ratio"].shift(1)
panel_df["gnpa_lag2"] = panel_df.groupby("bank_clean")["gnpa_ratio"].shift(2)
# Compute first differences only when year_diff == 1
est_feats = ["roa", "credit_growth_lag2", "cd_ratio", "pcr", "gdp_growth", "repo_rate"]
for col in ["gnpa_ratio", "gnpa_lag1"] + est_feats:
    panel_df[f"d_{col}"] = panel_df.groupby("bank_clean")[col].diff()
panel_df["year_lag1_diff"] = panel_df.groupby("bank_clean")["year_diff"].shift(1)

iv_df = panel_df[(panel_df["year_diff"] == 1) & (panel_df["year_lag1_diff"] == 1)].dropna(
    subset=["d_gnpa_ratio", "d_gnpa_lag1", "gnpa_lag2"] + [f"d_{c}" for c in est_feats]
).copy()
print(f"\n=== ANDERSON-HSIAO FD-IV2SLS (consecutive year obs = {len(iv_df)}, banks = {iv_df['bank_clean'].nunique()}) ===")
exog_cols = [f"d_{c}" for c in est_feats]
iv_mod = IV2SLS(
    dependent=iv_df["d_gnpa_ratio"],
    exog=iv_df[exog_cols],
    endog=iv_df[["d_gnpa_lag1"]],
    instruments=iv_df[["gnpa_lag2"]]
).fit(cov_type="clustered", clusters=iv_df["bank_clean"])
for k in iv_mod.params.index:
    print(f"  {k:22s}: coef={iv_mod.params[k]:.4f}, se={iv_mod.std_errors[k]:.4f}, p={iv_mod.pvalues[k]:.4f}")

# 4. Check Restored Bank-Group Stress Test (banking_panel.csv)
print("\n=== RESTORED BANK-GROUP STRESS TEST (banking_panel.csv) ===")
df_g = load_banking_panel()
ml_g = get_model_ready_frame(df_g)
print(group_reliability(ml_g))
fe_g = FixedEffectsRegressor().fit(ml_g)
latest_g = df_g[df_g["year"] == 2024].set_index("bank_group")
st_res = run_stress_test(fe_g, latest_g)
print("\nLinear FE Stress Test on Restored banking_panel.csv (n=40, PSB n=12):")
print(st_res)
boot_res = bootstrap_stress_test(ml_g, latest_g, n_boot=500)
print("\nTail Risk 90% Bootstrap CI on Restored banking_panel.csv:")
print(boot_res["Tail risk\n(COVID FY21)"])
