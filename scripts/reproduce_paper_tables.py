"""
Reproduce all empirical tables, diagnostics, confidence intervals, SHAP values,
and stress-test projections reported in the research paper from a single run.

Usage:
    python scripts/reproduce_paper_tables.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import numpy as np
import pandas as pd
import statsmodels.api as sm
from linearmodels.panel import PanelOLS
from scipy.stats import norm
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
)
from xgboost import XGBClassifier, XGBRegressor

from npa_ews import config
from npa_ews.data import (
    get_bank_level_model_ready,
    get_model_ready_frame,
    group_reliability,
    load_bank_level_panel,
    load_banking_panel,
)
from npa_ews.models.dynamic_panel import DynamicPanelEstimator
from npa_ews.models.panel_fe import FixedEffectsRegressor
from npa_ews.models.xgb_model import GnpaXGBModel, PcaBreachClassifier
from npa_ews.stress import (
    bootstrap_stress_test,
    run_stress_test,
    simulate_bank_capital_depletion,
)


def bootstrap_auc_ci(
    y_true: np.ndarray,
    scores: np.ndarray,
    n_boot: int = 2000,
    seed: int = config.RANDOM_SEED,
) -> tuple[float, float, float]:
    """Stratified-safe bootstrap 95% CI for ROC-AUC."""
    rng = np.random.default_rng(seed)
    base = float(roc_auc_score(y_true, scores))
    aucs = []
    n = len(y_true)
    for _ in range(n_boot):
        idx = rng.integers(0, n, size=n)
        if len(np.unique(y_true[idx])) < 2:
            continue
        aucs.append(float(roc_auc_score(y_true[idx], scores[idx])))
    lo, hi = np.percentile(aucs, [2.5, 97.5])
    return base, float(lo), float(hi)


def paired_bootstrap_auc_diff_pvalue(
    y_true: np.ndarray,
    scores_a: np.ndarray,
    scores_b: np.ndarray,
    n_boot: int = 2000,
    seed: int = config.RANDOM_SEED,
) -> float:
    """Two-sided paired bootstrap p-value testing H0: AUC(A) == AUC(B)."""
    rng = np.random.default_rng(seed)
    obs_diff = float(roc_auc_score(y_true, scores_a) - roc_auc_score(y_true, scores_b))
    diffs = []
    n = len(y_true)
    for _ in range(n_boot):
        idx = rng.integers(0, n, size=n)
        if len(np.unique(y_true[idx])) < 2:
            continue
        d = roc_auc_score(y_true[idx], scores_a[idx]) - roc_auc_score(y_true[idx], scores_b[idx])
        diffs.append(float(d))
    se = float(np.std(diffs))
    if se == 0:
        return 1.0
    z = obs_diff / se
    return float(2.0 * (1.0 - norm.cdf(abs(z))))


def main() -> None:
    print("=" * 80)
    print("NPA-EWS REPRODUCIBLE EMPIRICAL AUDIT (SINGLE-RUN OUTPUT)")
    print("=" * 80)

    # ------------------------------------------------------------------
    # SECTION III: DATASET SUMMARY (TIER 1 BANK-LEVEL + TIER 2 GROUP)
    # ------------------------------------------------------------------
    df_b = load_bank_level_panel()
    clean_b = get_bank_level_model_ready(df_b, features=config.BANK_LEVEL_FEATURES, target="gnpa_next1yr")
    clean_b = clean_b.dropna(subset=["pca_breach_next1yr"]).copy()

    print("\n--- SECTION III: TIER 1 BANK-LEVEL PANEL ---")
    print(f"Raw bank-level panel: {len(df_b)} rows, {df_b['bank_clean'].nunique()} unique banks, FY{df_b['year'].min()}-FY{df_b['year'].max()}")
    print(f"Model-ready panel:    {len(clean_b)} rows, {clean_b['bank_clean'].nunique()} unique banks, FY{clean_b['year'].min()}-FY{clean_b['year'].max()}")
    print("\nBreakdown by bank_group (model-ready):")
    grp_sum = clean_b.groupby("bank_group").agg(
        obs=("year", "count"),
        banks=("bank_clean", "nunique"),
        yr_min=("year", "min"),
        yr_max=("year", "max"),
    )
    print(grp_sum.to_string())

    df_g = load_banking_panel()
    ml_g = get_model_ready_frame(df_g)
    print("\n--- SECTION III: TIER 2 BANK-GROUP PANEL (RESTORED) ---")
    print(f"Raw group panel:   {len(df_g)} rows, {df_g['bank_group'].nunique()} groups, FY{df_g['year'].min()}-FY{df_g['year'].max()}")
    print(f"Model-ready panel: {len(ml_g)} rows, FY{ml_g['year'].min()}-FY{ml_g['year'].max()}")
    print(group_reliability(ml_g).to_string())

    # ------------------------------------------------------------------
    # TABLE I: ECONOMETRIC PANEL ESTIMATORS
    # ------------------------------------------------------------------
    est = DynamicPanelEstimator()
    stat_res = est.fit_static(clean_b)
    dyn_res = est.fit(clean_b)
    iv_res = est.fit_fd_iv(clean_b)

    print("\n--- TABLE I: ECONOMETRIC ESTIMATORS (BANK-LEVEL PANEL) ---")
    print(f"Static FE : N={stat_res.n_obs}, Banks={stat_res.n_entities}, Within R2={stat_res.r_squared:.3f}")
    print(f"Dynamic FE: N={dyn_res.n_obs}, Banks={dyn_res.n_entities}, Within R2={dyn_res.r_squared:.3f}")
    print(f"FD-IV2SLS : N={iv_res.n_obs}, Banks={iv_res.n_entities}, R2={iv_res.r_squared:.3f}")

    ordered_vars = ["gnpa_ratio_lag1", "roa", "credit_growth_lag2", "cd_ratio", "pcr", "gdp_growth", "repo_rate"]
    for v in ordered_vars:
        def fmt_res(res_obj):
            if v not in res_obj.params:
                return "---"
            c = res_obj.params[v]
            se = res_obj.std_errors[v]
            p = res_obj.pvalues[v]
            stars = "***" if p < 0.01 else ("**" if p < 0.05 else ("*" if p < 0.10 else ""))
            return f"{c:.3f}{stars} ({se:.3f})"
        print(f"  {v:20s} | {fmt_res(stat_res):22s} | {fmt_res(dyn_res):22s} | {fmt_res(iv_res):22s}")

    # ------------------------------------------------------------------
    # TABLE II: OUT-OF-TIME VALIDATION (REGIME A & REGIME B + NAIVE)
    # ------------------------------------------------------------------
    train = clean_b[clean_b["year"] <= config.TRAIN_YEAR_MAX].copy()
    test = clean_b[clean_b["year"] >= config.TEST_YEAR_MIN].copy()
    y_test_reg = test["gnpa_next1yr"].to_numpy()
    y_test_cls = test["pca_breach_next1yr"].astype(int).to_numpy()
    n_pos = int(y_test_cls.sum())
    n_onset = int(((test["gnpa_ratio"] < 6.0) & (test["pca_breach_next1yr"] == 1)).sum())
    n_recov = int(((test["gnpa_ratio"] >= 6.0) & (test["pca_breach_next1yr"] == 0)).sum())

    print(f"\n--- TABLE II: OUT-OF-TIME EVALUATION (Train <= {config.TRAIN_YEAR_MAX}: n={len(train)}, Test >= {config.TEST_YEAR_MIN}: n={len(test)}) ---")
    print(f"Test breaches (GNPA_t+1 >= 6%): {n_pos}/{len(test)} ({n_pos/len(test)*100:.1f}%), New onsets: {n_onset}, Recoveries: {n_recov}")

    feats_cov = config.BANK_LEVEL_FEATURES
    feats_full = ["gnpa_ratio"] + config.BANK_LEVEL_FEATURES

    # Naive baselines
    naive_reg = test["gnpa_ratio"].to_numpy()
    naive_cls_score = test["gnpa_ratio"].to_numpy() / 100.0
    naive_cls_pred = (test["gnpa_ratio"] >= 6.0).astype(int).to_numpy()

    # Regime A (Covariates only, matching config.BANK_LEVEL_FEATURES)
    X_tr_a = sm.add_constant(train[feats_cov])
    X_te_a = sm.add_constant(test[feats_cov], has_constant="add")
    ols_a_reg = sm.OLS(train["gnpa_next1yr"], X_tr_a).fit().predict(X_te_a[X_tr_a.columns]).to_numpy()

    tr_fe = train.set_index(["bank_clean", "year"])
    fe_fit = PanelOLS(tr_fe["gnpa_next1yr"], tr_fe[feats_cov], entity_effects=True).fit()
    ent_eff = fe_fit.estimated_effects.groupby(level=0).mean()["estimated_effects"]
    fe_a_reg = (test[feats_cov].to_numpy() @ fe_fit.params.to_numpy()) + test["bank_clean"].map(ent_eff).fillna(ent_eff.mean()).to_numpy()

    rf_a_reg = RandomForestRegressor(n_estimators=100, max_depth=5, random_state=config.RANDOM_SEED).fit(train[feats_cov], train["gnpa_next1yr"]).predict(test[feats_cov])
    xgb_a_reg = GnpaXGBModel(features=feats_cov, target="gnpa_next1yr").fit(train, test).predict(test)

    logit_a = LogisticRegression(max_iter=1000, random_state=config.RANDOM_SEED).fit(train[feats_cov], train["pca_breach_next1yr"].astype(int))
    logit_a_p = logit_a.predict_proba(test[feats_cov])[:, 1]
    rf_a_cls = RandomForestClassifier(n_estimators=100, max_depth=4, random_state=config.RANDOM_SEED).fit(train[feats_cov], train["pca_breach_next1yr"].astype(int))
    rf_a_p = rf_a_cls.predict_proba(test[feats_cov])[:, 1]
    xgb_a_cls = PcaBreachClassifier(features=feats_cov, target="pca_breach_next1yr").fit(train)
    xgb_a_p = xgb_a_cls.predict_proba(test)

    # Regime B (Full Information: adding gnpa_ratio)
    X_tr_b = sm.add_constant(train[feats_full])
    X_te_b = sm.add_constant(test[feats_full], has_constant="add")
    ols_b_reg = sm.OLS(train["gnpa_next1yr"], X_tr_b).fit().predict(X_te_b[X_tr_b.columns]).to_numpy()
    rf_b_reg = RandomForestRegressor(n_estimators=100, max_depth=4, random_state=config.RANDOM_SEED).fit(train[feats_full], train["gnpa_next1yr"]).predict(test[feats_full])
    xgb_b_reg = XGBRegressor(n_estimators=100, max_depth=3, learning_rate=0.05, subsample=0.8, random_state=config.RANDOM_SEED).fit(train[feats_full], train["gnpa_next1yr"]).predict(test[feats_full])

    logit_b = LogisticRegression(max_iter=1000, random_state=config.RANDOM_SEED).fit(train[feats_full], train["pca_breach_next1yr"].astype(int))
    logit_b_p = logit_b.predict_proba(test[feats_full])[:, 1]
    rf_b_cls = RandomForestClassifier(n_estimators=100, max_depth=4, random_state=config.RANDOM_SEED).fit(train[feats_full], train["pca_breach_next1yr"].astype(int))
    rf_b_p = rf_b_cls.predict_proba(test[feats_full])[:, 1]
    xgb_b_cls = XGBClassifier(n_estimators=100, max_depth=3, learning_rate=0.05, subsample=0.8, eval_metric="logloss", random_state=config.RANDOM_SEED).fit(train[feats_full], train["pca_breach_next1yr"].astype(int))
    xgb_b_p = xgb_b_cls.predict_proba(test[feats_full])[:, 1]

    print("\n[Table II-A: Continuous Level Forecasting (n=156)]")
    for label, preds in [
        ("Naive Persistence (GNPA_t)", naive_reg),
        ("Regime A (No GNPA_t): Pooled OLS", ols_a_reg),
        ("Regime A (No GNPA_t): Panel FE", fe_a_reg),
        ("Regime A (No GNPA_t): Random Forest", rf_a_reg),
        ("Regime A (No GNPA_t): XGBoost", xgb_a_reg),
        ("Regime B (With GNPA_t): Pooled OLS", ols_b_reg),
        ("Regime B (With GNPA_t): Random Forest", rf_b_reg),
        ("Regime B (With GNPA_t): XGBoost", xgb_b_reg),
    ]:
        print(f"  {label:38s}: MAE={mean_absolute_error(y_test_reg, preds):.2f}%, RMSE={np.sqrt(mean_squared_error(y_test_reg, preds)):.2f}%, R2={r2_score(y_test_reg, preds):.3f}")

    print("\n[Table II-B: PCA Breach Proxy Classification (n=156, pos=22)]")
    cls_rows = [
        ("Naive Persistence (GNPA_t >= 6%)", naive_cls_score, naive_cls_pred),
        ("Regime A (No GNPA_t): Logit", logit_a_p, (logit_a_p >= 0.5).astype(int)),
        ("Regime A (No GNPA_t): Random Forest", rf_a_p, (rf_a_p >= 0.5).astype(int)),
        ("Regime A (No GNPA_t): XGBoost", xgb_a_p, (xgb_a_p >= 0.5).astype(int)),
        ("Regime B (With GNPA_t): Logit", logit_b_p, (logit_b_p >= 0.5).astype(int)),
        ("Regime B (With GNPA_t): Random Forest", rf_b_p, (rf_b_p >= 0.5).astype(int)),
        ("Regime B (With GNPA_t): XGBoost", xgb_b_p, (xgb_b_p >= 0.5).astype(int)),
    ]
    for label, prob, pred in cls_rows:
        auc, lo, hi = bootstrap_auc_ci(y_test_cls, prob)
        acc = accuracy_score(y_test_cls, pred) * 100
        prec = precision_score(y_test_cls, pred, zero_division=0) * 100
        rec = recall_score(y_test_cls, pred, zero_division=0) * 100
        f1 = f1_score(y_test_cls, pred, zero_division=0)
        tn, fp, fn, tp = confusion_matrix(y_test_cls, pred).ravel()
        print(f"  {label:38s}: AUC={auc:.3f} [{lo:.3f},{hi:.3f}], Acc={acc:.1f}%, Prec={prec:.1f}%, Rec={rec:.1f}%, F1={f1:.3f} (TP={tp}/22)")

    p_xgb_vs_logit_a = paired_bootstrap_auc_diff_pvalue(y_test_cls, xgb_a_p, logit_a_p)
    p_naive_vs_xgb_b = paired_bootstrap_auc_diff_pvalue(y_test_cls, naive_cls_score, xgb_b_p)
    print(f"\nPaired bootstrap p-value (Regime A XGBoost vs Logit): p = {p_xgb_vs_logit_a:.3f}")
    print(f"Paired bootstrap p-value (Naive vs Regime B XGBoost): p = {p_naive_vs_xgb_b:.3f}")

    # ------------------------------------------------------------------
    # SHAP FEATURE IMPORTANCE (REGIME A COVARIATE MODEL)
    # ------------------------------------------------------------------
    print("\n--- SECTION V.C: TREESHAP GLOBAL IMPORTANCE (COVARIATE-ONLY CLASSIFIER) ---")
    print(xgb_a_cls.global_importance(clean_b).round(3).to_string())

    # ------------------------------------------------------------------
    # TABLE III: MACRO STRESS TEST (TIER 2 RESTORED BANK-GROUP PANEL)
    # ------------------------------------------------------------------
    fe_g = FixedEffectsRegressor().fit(ml_g)
    latest_g = df_g[df_g["year"] == 2024].set_index("bank_group")
    st_pt = run_stress_test(fe_g, latest_g)
    boot = bootstrap_stress_test(ml_g, latest_g, n_boot=1000)

    print("\n--- TABLE III: BANK-GROUP MACRO STRESS TEST (RESTORED TIER 2 PANEL, N=40) ---")
    print("Point Estimates:")
    print(st_pt.round(2).to_string())
    tail_key = [k for k in boot.keys() if "Tail" in k][0]
    print("\nTail Risk Bootstrap Uncertainty (1,000 block-bootstrap draws):")
    print(boot[tail_key].to_string())

    # Bank-level 2024 cross-section capital depletion check
    b2024 = df_b[df_b["year"] == 2024].dropna(subset=["gnpa_ratio", "gross_adv_cr", "crar"]).copy()
    gnpa_shock_pp = float(st_pt.iloc[:, -1].iloc[0] - st_pt.iloc[:, 0].iloc[0])
    cap_df = simulate_bank_capital_depletion(b2024, gnpa_increase_pct=gnpa_shock_pp)
    print(f"\n--- BANK-LEVEL 2024 CAPITAL DEPLETION CHECK (n={len(cap_df)} banks, +{gnpa_shock_pp:.2f} pp shock) ---")
    print(cap_df.groupby("bank_group").agg(
        banks=("bank_clean", "count"),
        base_gnpa=("gnpa_ratio", "mean"),
        stressed_gnpa=("stressed_gnpa", "mean"),
        base_crar=("crar", "mean"),
        stressed_crar=("stressed_crar", "mean"),
        crar_drop=("crar_depletion_pp", "mean"),
        breaches_9pct=("crar_breach_9pct", "sum"),
    ).round(2).to_string())


if __name__ == "__main__":
    main()
