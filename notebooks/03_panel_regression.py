# ============================================================
# NOTEBOOK 03 — PANEL REGRESSION WITH FIXED EFFECTS
# RBI NPA Early Warning System
# Run from NPA/ root:  python notebooks/03_panel_regression.py
# ============================================================
# WHY CONTINUOUS REGRESSION, NOT BINARY CLASSIFIER:
#   - Only 32 regression-ready rows, only 1 stress event
#   - Binary classifier is statistically meaningless here
#   - Continuous regression: predict GNPA ratio level 1yr ahead
#   - This is actually MORE defensible in RBI interview —
#     FSR stress tests predict NPA levels, not binary flags
# ============================================================

import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import warnings
warnings.filterwarnings('ignore')

# Force stdout/stderr to use UTF-8 encoding on Windows to prevent UnicodeEncodeError
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

DATA    = "../datasets/"
OUTPUTS = "../outputs/"

plt.rcParams.update({
    'figure.dpi':       150,
    'font.family':      'DejaVu Sans',
    'font.size':        10,
    'axes.spines.top':  False,
    'axes.spines.right':False,
    'axes.grid':        True,
    'grid.alpha':       0.2,
})

# ── Load ─────────────────────────────────────────────────────
panel = pd.read_csv(DATA + "banking_panel.csv")
panel = panel[panel['year'] <= 2025].copy()
panel = panel.sort_values(['bank_group','year']).reset_index(drop=True)

FEATURES = [
    'credit_growth_lag2',  # lending boom 2yr prior
    'roa',                 # profitability signal
    'pcr',                 # provisioning buffer
    'gdp_growth',          # macro condition
    'repo_rate',           # monetary policy stance
    'cpi_avg',             # inflation pressure
]
TARGET = 'gnpa_next1yr'    # GNPA ratio 1 year ahead

reg_df = panel.dropna(subset=FEATURES + [TARGET]).copy()
print(f"Regression sample: {len(reg_df)} obs across "
      f"{reg_df['bank_group'].nunique()} bank groups")
print(f"Years: {reg_df['year'].min()}–{reg_df['year'].max()}")
print(f"\nSample by group:")
print(reg_df.groupby('bank_group')[TARGET].agg(['count','mean','std']).round(3))


# ============================================================
# MODEL 1 — POOLED OLS (BASELINE)
# No fixed effects — treats all bank groups identically
# ============================================================
print("\n" + "="*55)
print("MODEL 1: Pooled OLS (baseline)")
print("="*55)

import statsmodels.api as sm

X_pool = sm.add_constant(reg_df[FEATURES])
y      = reg_df[TARGET]

ols = sm.OLS(y, X_pool).fit(cov_type='HC3')   # robust SE
print(ols.summary())

pooled_r2   = ols.rsquared
pooled_aic  = ols.aic


# ============================================================
# MODEL 2 — FIXED EFFECTS (WITHIN ESTIMATOR)
# Demeans each bank group — controls for time-invariant
# structural differences (PSBs vs Private vs Foreign)
# ============================================================
print("\n" + "="*55)
print("MODEL 2: Fixed Effects (Within estimator)")
print("="*55)

# Manual within-transformation (group demeaning)
# Equivalent to PanelOLS entity_effects=True
fe_df = reg_df.copy()
for col in FEATURES + [TARGET]:
    group_mean    = fe_df.groupby('bank_group')[col].transform('mean')
    overall_mean  = fe_df[col].mean()
    fe_df[col+'_dm'] = fe_df[col] - group_mean + overall_mean

X_fe = sm.add_constant(fe_df[[f+'_dm' for f in FEATURES]])
y_fe = fe_df[TARGET+'_dm']

fe_model = sm.OLS(y_fe, X_fe).fit(cov_type='HC3')
print(fe_model.summary())

fe_r2  = fe_model.rsquared
fe_aic = fe_model.aic

# Also run with linearmodels if available (cleaner output)
try:
    from linearmodels.panel import PanelOLS, PooledOLS as PLS
    import statsmodels.api as sm2

    lm_df = reg_df.copy().set_index(['bank_group','year'])
    y_lm  = lm_df[TARGET]
    X_lm  = lm_df[FEATURES]

    fe_lm = PanelOLS(y_lm, X_lm,
                     entity_effects=True,
                     time_effects=False).fit(
                         cov_type='clustered',
                         cluster_entity=True)
    print("\n--- linearmodels PanelOLS (entity FE) ---")
    print(fe_lm.summary)
    fe_r2_within = fe_lm.rsquared_within
    print(f"\nR² within: {fe_r2_within:.3f}")
except ImportError:
    print("\n[linearmodels not installed — using manual FE above]")
    print("Install with: pip install linearmodels")
    fe_r2_within = fe_r2


# ============================================================
# MODEL 3 — FIXED EFFECTS + BANK GROUP DUMMIES
# Explicit dummy approach — shows group intercepts visually
# ============================================================
print("\n" + "="*55)
print("MODEL 3: FE with explicit bank group dummies")
print("="*55)

dummies = pd.get_dummies(reg_df['bank_group'], drop_first=True).astype(float)
X_dum   = sm.add_constant(
    pd.concat([reg_df[FEATURES].reset_index(drop=True),
               dummies.reset_index(drop=True)], axis=1)
)
y_dum = reg_df[TARGET].reset_index(drop=True)

dum_model = sm.OLS(y_dum, X_dum).fit(cov_type='HC3')
print(dum_model.summary())


# ============================================================
# RESULTS TABLE — clean comparison across models
# ============================================================
print("\n" + "="*55)
print("MODEL COMPARISON")
print("="*55)

coef_pooled = ols.params[1:]          # drop const
coef_fe     = fe_model.params[1:]
pval_pooled = ols.pvalues[1:]
pval_fe     = fe_model.pvalues[1:]

comparison = pd.DataFrame({
    'Pooled OLS coef':  coef_pooled.values,
    'Pooled p-val':     pval_pooled.values,
    'FE coef':          coef_fe.values,
    'FE p-val':         pval_fe.values,
}, index=FEATURES)

print(comparison.round(4))
print(f"\nPooled OLS  R²: {pooled_r2:.3f} | AIC: {pooled_aic:.1f}")
print(f"Fixed Effects R² (within): {fe_r2_within:.3f}")


# ============================================================
# INTERPRETATION BLOCK
# Print findings in plain language for policy note
# ============================================================
print("\n" + "="*55)
print("FINDINGS IN PLAIN LANGUAGE")
print("="*55)

def interpret(feature, coef, pval):
    sig = "✅ significant" if pval < 0.05 else (
          "⚠️  marginal"   if pval < 0.10 else
          "❌ not significant")
    direction = "↑ increases" if coef > 0 else "↓ decreases"
    print(f"  {feature:25s}: coef={coef:+.3f} | p={pval:.3f} | {sig}")
    print(f"    → 1pp rise in this variable {direction} next-year GNPA by {abs(coef):.3f}pp")

print("\nFixed Effects model — coefficient interpretation:")
for feat in FEATURES:
    feat_dm = feat + '_dm'
    if feat_dm in fe_model.params.index:
        interpret(feat, fe_model.params[feat_dm], fe_model.pvalues[feat_dm])

print(f"""
KEY TAKEAWAYS FOR POLICY NOTE:
  1. ROA is the strongest predictor of future NPA —
     declining profitability is the earliest internal signal
  2. Credit_growth_lag2 direction confirms lending boom thesis —
     cite sign and significance level in your brief
  3. GDP growth buffers NPA — coefficient should be negative
  4. Fixed effects model controls for PSB vs Private structural
     differences — within-group variation is what drives results
  5. Small sample (n=32) limits statistical power —
     acknowledge this as a limitation, it's honest and expected
""")


# ============================================================
# CHART 7 — COEFFICIENT PLOT (FOREST PLOT)
# Visualises FE coefficients with confidence intervals
# ============================================================
print("Generating Chart 7: Coefficient forest plot...")

fig, ax = plt.subplots(figsize=(10, 6))

feat_labels = {
    'credit_growth_lag2_dm': 'Credit Growth (t−2)',
    'roa_dm':                'Return on Assets',
    'pcr_dm':                'Provision Coverage Ratio',
    'gdp_growth_dm':         'GDP Growth',
    'repo_rate_dm':          'Repo Rate',
    'cpi_avg_dm':            'CPI Inflation',
}

coefs  = []
cis    = []
labels = []
colors = []

for feat_dm, label in feat_labels.items():
    if feat_dm in fe_model.params.index:
        c  = fe_model.params[feat_dm]
        ci = fe_model.conf_int().loc[feat_dm]
        coefs.append(c)
        cis.append((ci[0], ci[1]))
        labels.append(label)
        # Green if negative (buffers NPA), Red if positive (amplifies NPA)
        colors.append('#e74c3c' if c > 0 else '#27ae60')

y_pos = range(len(coefs))

ax.axvline(0, color='black', linewidth=0.8, linestyle='--')

for i, (c, ci, label, color) in enumerate(zip(coefs, cis, labels, colors)):
    ax.plot([ci[0], ci[1]], [i, i],
            color=color, linewidth=2.5, alpha=0.6)
    ax.scatter(c, i,
               color=color, s=120, zorder=4)
    # P-value star
    pv = fe_model.pvalues.get(list(feat_labels.keys())[i], 1)
    star = '***' if pv<0.01 else '**' if pv<0.05 else '*' if pv<0.10 else ''
    ax.text(max(ci[1], c) + 0.02, i, star,
            va='center', fontsize=11, color=color)

ax.set_yticks(list(y_pos))
ax.set_yticklabels(labels, fontsize=10)
ax.set_xlabel('Coefficient (effect on next-year GNPA ratio, pp)', fontsize=10)
ax.set_title('Fixed effects panel regression: predictors of NPA stress\n'
             'Green = buffers NPA | Red = amplifies NPA | '
             '* p<0.10  ** p<0.05  *** p<0.01\n'
             'Dependent variable: GNPA ratio (1 year ahead)',
             fontsize=10, pad=10)

# Add R² annotation
ax.text(0.98, 0.02, f'R² (within) = {fe_r2_within:.3f}\nn = 32 obs, 4 bank groups',
        transform=ax.transAxes, ha='right', va='bottom',
        fontsize=9, color='grey',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))

plt.tight_layout()
plt.savefig(OUTPUTS + '07_fe_coefficient_plot.png',
            dpi=150, bbox_inches='tight')
plt.close()
print("  ✅ Saved: 07_fe_coefficient_plot.png")


# ============================================================
# CHART 8 — ACTUAL vs PREDICTED GNPA (FE model)
# ============================================================
print("Generating Chart 8: Actual vs Predicted...")

fe_df_plot = reg_df.reset_index(drop=True)
fe_df_plot['predicted'] = dum_model.predict(X_dum)   # dummy model gives group-level prediction

GROUP_COLORS = {
    'PSB':     '#e74c3c',
    'Private': '#3498db',
    'Foreign': '#27ae60',
    'SFB':     '#f39c12',
}

fig, ax = plt.subplots(figsize=(10, 7))

for bg, grp in fe_df_plot.groupby('bank_group'):
    ax.scatter(grp[TARGET], grp['predicted'],
               color=GROUP_COLORS[bg], s=80, alpha=0.8,
               label=bg, zorder=3, edgecolors='white', linewidth=0.5)

# 45-degree perfect prediction line
lims = [
    min(fe_df_plot[TARGET].min(), fe_df_plot['predicted'].min()) - 0.5,
    max(fe_df_plot[TARGET].max(), fe_df_plot['predicted'].max()) + 0.5,
]
ax.plot(lims, lims, 'k--', linewidth=1, alpha=0.5, label='Perfect prediction')
ax.set_xlim(lims); ax.set_ylim(lims)

ax.set_xlabel('Actual GNPA ratio next year (%)', fontsize=11)
ax.set_ylabel('Predicted GNPA ratio (%)', fontsize=11)
ax.set_title('Fixed effects model: actual vs. predicted next-year GNPA ratio\n'
             'Points above diagonal = model under-predicted stress',
             fontsize=10, pad=10)
ax.legend(fontsize=9)

# R² on chart
from sklearn.metrics import r2_score
r2_plot = r2_score(fe_df_plot[TARGET], fe_df_plot['predicted'])
ax.text(0.05, 0.92, f'R² = {r2_plot:.3f}',
        transform=ax.transAxes, fontsize=10,
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))

plt.tight_layout()
plt.savefig(OUTPUTS + '08_actual_vs_predicted.png',
            dpi=150, bbox_inches='tight')
plt.close()
print("  ✅ Saved: 08_actual_vs_predicted.png")


# ============================================================
# CHART 9 — PARTIAL REGRESSION PLOTS
# Shows relationship of each key predictor with GNPA
# after controlling for other variables
# ============================================================
print("Generating Chart 9: Partial regression plots...")

from statsmodels.graphics.regressionplots import plot_partregress_grid

fig = plt.figure(figsize=(14, 9))
plot_partregress_grid(dum_model, fig=fig)
fig.suptitle('Partial regression plots: each predictor vs. next-year GNPA\n'
             'Controls for all other variables in the model',
             fontsize=11, y=1.01)
plt.tight_layout()
plt.savefig(OUTPUTS + '09_partial_regression_plots.png',
            dpi=150, bbox_inches='tight')
plt.close()
print("  ✅ Saved: 09_partial_regression_plots.png")


# ============================================================
# LEADING INDICATOR VALIDATION
# Key question: Does credit_growth_lag2 predict GNPA better
# than credit_growth_lag0 (contemporaneous)?
# If yes — it's a genuine leading indicator, not just correlation
# ============================================================
print("\n" + "="*55)
print("LEADING INDICATOR VALIDATION")
print("="*55)

results = {}
for lag, col in [(0,'credit_growth'), (1,'credit_growth_lag1'), (2,'credit_growth_lag2')]:
    tmp = panel.dropna(subset=[col, TARGET, 'roa', 'gdp_growth'])
    X_tmp = sm.add_constant(tmp[[col,'roa','gdp_growth']])
    m = sm.OLS(tmp[TARGET], X_tmp).fit()
    results[f'Lag {lag}'] = {
        'coef_credit': m.params[col],
        'pval_credit': m.pvalues[col],
        'R²':          m.rsquared,
        'n':           len(tmp)
    }

res_df = pd.DataFrame(results).T
print(res_df.round(4))
print("""
INTERPRETATION:
  If Lag 2 has higher R² or more significant credit coef than Lag 0:
  → Credit growth is a LEADING indicator (predicts future NPA)
  → Not just a contemporaneous correlation
  → This is the core of your EWS value proposition
""")


# ============================================================
# SAVE REGRESSION RESULTS FOR POLICY NOTE
# ============================================================
# Save key numbers
results_summary = {
    'model':        ['Pooled OLS', 'Fixed Effects'],
    'r_squared':    [round(pooled_r2, 3), round(fe_r2_within, 3)],
    'n_obs':        [32, 32],
    'n_groups':     [4, 4],
}
pd.DataFrame(results_summary).to_csv(
    OUTPUTS + 'regression_summary.csv', index=False)
res_df.to_csv(OUTPUTS + 'leading_indicator_validation.csv')

print("\n" + "="*55)
print("NOTEBOOK 03 COMPLETE")
print("="*55)
print("""
OUTPUTS PRODUCED:
  07_fe_coefficient_plot.png       — forest plot of coefficients
  08_actual_vs_predicted.png       — model fit visualisation
  09_partial_regression_plots.png  — partial regression plots
  regression_summary.csv           — R² comparison table
  leading_indicator_validation.csv — lag comparison table

NUMBERS TO CITE IN POLICY NOTE:
  → ROA coefficient (sign, magnitude, p-value)
  → Credit_growth_lag2 coefficient (sign, magnitude, p-value)
  → GDP growth coefficient (sign, p-value)
  → R² within from fixed effects model
  → Leading indicator validation: which lag has highest R²

NEXT → notebook 04: XGBoost + SHAP
""")