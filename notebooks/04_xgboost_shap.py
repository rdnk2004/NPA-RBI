# ============================================================
# NOTEBOOK 04 — XGBoost + SHAP
# RBI NPA Early Warning System
# Run from NPA/ root:  python notebooks/04_xgboost_shap.py
# ============================================================
# DESIGN DECISIONS (say these in interview):
#   - Continuous regression (predict GNPA level), not binary
#   - Temporal train/test split: train ≤2021, test ≥2022
#   - Shallow trees (max_depth=2) to prevent overfitting on n=32
#   - SHAP for explainability — supervisory-grade transparency
#   - Small sample → model is pattern-identifier, not predictor
# ============================================================

import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
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

GROUP_COLORS = {
    'PSB':     '#e74c3c',
    'Private': '#3498db',
    'Foreign': '#27ae60',
    'SFB':     '#f39c12',
}

# ── Load ─────────────────────────────────────────────────────
panel = pd.read_csv(DATA + "banking_panel.csv")
panel = panel[panel['year'] <= 2025].copy()
panel = panel.sort_values(['bank_group','year']).reset_index(drop=True)

FEATURES = ['credit_growth_lag2','roa','pcr','gdp_growth','repo_rate','cpi_avg']
TARGET   = 'gnpa_next1yr'

FEAT_LABELS = {
    'credit_growth_lag2': 'Credit Growth (t−2)',
    'roa':                'Return on Assets',
    'pcr':                'Provision Coverage Ratio',
    'gdp_growth':         'GDP Growth',
    'repo_rate':          'Repo Rate',
    'cpi_avg':            'CPI Inflation',
}

ml_df = panel.dropna(subset=FEATURES+[TARGET]).copy()
ml_df = ml_df.sort_values(['bank_group','year']).reset_index(drop=True)

# ── Train / Test split (temporal) ────────────────────────────
train = ml_df[ml_df['year'] <= 2021].copy()
test  = ml_df[ml_df['year'] >= 2022].copy()

X_train = train[FEATURES]
y_train = train[TARGET]
X_test  = test[FEATURES]
y_test  = test[TARGET]

print(f"Train: {len(train)} obs ({train['year'].min()}–{train['year'].max()})")
print(f"Test:  {len(test)} obs  ({test['year'].min()}–{test['year'].max()})")


# ============================================================
# MODEL — XGBoost Regressor
# ============================================================
import xgboost as xgb
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

xgb_model = xgb.XGBRegressor(
    n_estimators       = 100,
    max_depth          = 2,       # shallow — prevents overfitting on n=32
    learning_rate      = 0.05,
    subsample          = 0.8,
    colsample_bytree   = 0.8,
    min_child_weight   = 3,       # conservative split
    reg_alpha          = 0.5,     # L1 regularisation
    reg_lambda         = 1.0,     # L2 regularisation
    random_state       = 42,
    verbosity          = 0,
)

xgb_model.fit(
    X_train, y_train,
    eval_set=[(X_test, y_test)],
    verbose=False,
)

# ── Evaluation ───────────────────────────────────────────────
y_pred_test  = xgb_model.predict(X_test)
y_pred_train = xgb_model.predict(X_train)

rmse_test = np.sqrt(mean_squared_error(y_test, y_pred_test))
mae_test  = mean_absolute_error(y_test, y_pred_test)
r2_test   = r2_score(y_test, y_pred_test)
r2_train  = r2_score(y_train, y_pred_train)

print(f"\n=== XGBoost Performance ===")
print(f"Train R²:  {r2_train:.3f}")
print(f"Test  R²:  {r2_test:.3f}")
print(f"Test RMSE: {rmse_test:.3f} pp")
print(f"Test MAE:  {mae_test:.3f} pp")

# Residuals
test = test.copy()
test['predicted'] = y_pred_test
test['residual']  = test[TARGET] - test['predicted']
print(f"\nTest residuals by group:")
print(test.groupby('bank_group')[['residual']].agg(['mean','std']).round(3))


# ============================================================
# SHAP EXPLANATIONS
# ============================================================
import shap

explainer   = shap.TreeExplainer(xgb_model)
shap_all    = explainer.shap_values(ml_df[FEATURES])
shap_test   = explainer.shap_values(X_test)
shap_train  = explainer.shap_values(X_train)
base_value  = explainer.expected_value

print(f"\nSHAP base value (mean prediction): {base_value:.3f}%")


# ============================================================
# CHART 10 — SHAP SUMMARY BAR (Global importance)
# ============================================================
print("\nGenerating Chart 10: SHAP global importance...")

mean_abs_shap = pd.Series(
    np.abs(shap_all).mean(axis=0),
    index=FEATURES
).sort_values(ascending=True)

fig, ax = plt.subplots(figsize=(9, 5))
colors_bar = ['#e74c3c' if f in ['cpi_avg','repo_rate','credit_growth_lag2']
              else '#27ae60' for f in mean_abs_shap.index]

bars = ax.barh(
    [FEAT_LABELS[f] for f in mean_abs_shap.index],
    mean_abs_shap.values,
    color=colors_bar, alpha=0.85, edgecolor='white'
)

# Value labels
for bar, val in zip(bars, mean_abs_shap.values):
    ax.text(val + 0.002, bar.get_y() + bar.get_height()/2,
            f'{val:.3f}', va='center', fontsize=9)

ax.set_xlabel('Mean |SHAP value| (average impact on GNPA prediction, pp)')
ax.set_title('XGBoost + SHAP: global feature importance\n'
             'Average absolute contribution to next-year GNPA prediction\n'
             'Green = reduces NPA prediction | Red = raises NPA prediction',
             fontsize=10, pad=10)
ax.set_xlim(0, mean_abs_shap.max() * 1.25)

# Legend
green_p = mpatches.Patch(color='#27ae60', alpha=0.85, label='Buffers NPA (reduces prediction)')
red_p   = mpatches.Patch(color='#e74c3c', alpha=0.85, label='Amplifies NPA (raises prediction)')
ax.legend(handles=[green_p, red_p], fontsize=8, loc='lower right')

plt.tight_layout()
plt.savefig(OUTPUTS + '10_shap_global_importance.png',
            dpi=150, bbox_inches='tight')
plt.close()
print("  ✅ Saved: 10_shap_global_importance.png")


# ============================================================
# CHART 11 — SHAP BEESWARM (Direction + magnitude)
# ============================================================
print("Generating Chart 11: SHAP beeswarm...")

shap_exp = shap.Explanation(
    values     = shap_all,
    base_values= np.full(len(ml_df), base_value),
    data       = ml_df[FEATURES].values,
    feature_names=[FEAT_LABELS[f] for f in FEATURES]
)

fig, ax = plt.subplots(figsize=(10, 6))
shap.plots.beeswarm(shap_exp, show=False, max_display=6, ax=ax, plot_size=None)
ax.set_title('SHAP beeswarm: feature direction and magnitude\n'
             'Red = high feature value | Blue = low feature value\n'
             'X-axis: SHAP value = contribution to GNPA prediction (pp)',
             fontsize=10, pad=8)
plt.tight_layout()
plt.savefig(OUTPUTS + '11_shap_beeswarm.png',
            dpi=150, bbox_inches='tight')
plt.close()
print("  ✅ Saved: 11_shap_beeswarm.png")


# ============================================================
# CHART 12 — SHAP FORCE PLOTS (Individual predictions)
# Two key cases:
#   A) PSB 2021 — highest stress in test period
#   B) Foreign 2023 — lowest stress in test period
# ============================================================
print("Generating Chart 12: SHAP force plots...")

# Find indices
psb_stress  = test[(test['bank_group']=='PSB')].sort_values(TARGET, ascending=False)
for_low     = test[(test['bank_group']=='Foreign')].sort_values(TARGET, ascending=True)

fig, axes = plt.subplots(2, 1, figsize=(13, 8))

for ax_i, (row_df, title) in enumerate([
    (psb_stress.iloc[[0]], 'PSB (highest stress in test set) — model explains high GNPA prediction'),
    (for_low.iloc[[0]],    'Foreign Banks (lowest stress in test set) — model explains low GNPA prediction'),
]):
    idx_in_test = row_df.index[0]
    # Get position in X_test
    pos = test.index.get_loc(idx_in_test)

    sv   = shap_test[pos]
    data = X_test.iloc[pos]
    pred = y_pred_test[pos]
    actual = y_test.iloc[pos]

    feat_names = [FEAT_LABELS[f] for f in FEATURES]
    feat_vals  = [f'{data[f]:.2f}' for f in FEATURES]

    # Sorted by |SHAP|
    order = np.argsort(np.abs(sv))[::-1]

    ax = axes[ax_i]
    colors = ['#e74c3c' if s > 0 else '#27ae60' for s in sv[order]]
    bars   = ax.barh(
        [f'{feat_names[i]}\n= {feat_vals[i]}' for i in order],
        sv[order], color=colors, alpha=0.85, edgecolor='white'
    )
    ax.axvline(0, color='black', linewidth=0.8)
    ax.set_xlabel('SHAP value (pp contribution to GNPA prediction)')
    ax.set_title(f'{title}\n'
                 f'Actual GNPA next year: {actual:.2f}% | '
                 f'Predicted: {pred:.2f}% | '
                 f'Base: {base_value:.2f}%',
                 fontsize=9)

    # Value labels
    for bar, val in zip(bars, sv[order]):
        offset = 0.003 if val >= 0 else -0.003
        ha     = 'left' if val >= 0 else 'right'
        ax.text(val + offset, bar.get_y() + bar.get_height()/2,
                f'{val:+.3f}pp', va='center', ha=ha, fontsize=8)

plt.suptitle('SHAP force plots: explaining individual NPA predictions\n'
             'Red bars = push prediction UP | Green bars = push prediction DOWN',
             fontsize=11, y=1.01)
plt.tight_layout()
plt.savefig(OUTPUTS + '12_shap_force_plots.png',
            dpi=150, bbox_inches='tight')
plt.close()
print("  ✅ Saved: 12_shap_force_plots.png")


# ============================================================
# CHART 13 — EWS DASHBOARD (Traffic light table)
# Most recent year prediction for each bank group
# ============================================================
print("Generating Chart 13: EWS dashboard...")

# Predict for 2024 (latest with full features)
latest_df = panel[panel['year']==2024].dropna(subset=FEATURES).copy()

if len(latest_df) > 0:
    latest_pred = xgb_model.predict(latest_df[FEATURES])
    latest_shap = explainer.shap_values(latest_df[FEATURES])

    latest_df = latest_df.reset_index(drop=True)
    latest_df['predicted_gnpa_2025'] = latest_pred

    def traffic(p):
        if p >= 7.0:  return 'HIGH ALERT'
        elif p >= 5.0: return 'WATCH'
        elif p >= 3.0: return 'ELEVATED'
        else:          return 'NORMAL'

    latest_df['signal'] = latest_df['predicted_gnpa_2025'].apply(traffic)

    # Top driver from SHAP
    top_driver = []
    for i in range(len(latest_df)):
        top_i = np.argmax(np.abs(latest_shap[i]))
        direction = '↑' if latest_shap[i][top_i] > 0 else '↓'
        top_driver.append(f"{FEAT_LABELS[FEATURES[top_i]]} {direction}")
    latest_df['top_driver'] = top_driver

    dash_cols = ['bank_group','gnpa_ratio','predicted_gnpa_2025','signal','top_driver']
    dashboard = latest_df[dash_cols].sort_values(
        'predicted_gnpa_2025', ascending=False)

    print("\n" + "="*65)
    print("RBI OFFSITE SURVEILLANCE — NPA EARLY WARNING DASHBOARD")
    print(f"Reference: 2024 data → Predicting 2025 GNPA stress")
    print("="*65)
    print(dashboard.to_string(index=False))
    print("="*65)

    dashboard.to_csv(OUTPUTS + 'ews_dashboard_2025.csv', index=False)
    print("\n  ✅ Saved: ews_dashboard_2025.csv")

    # Visual dashboard
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.axis('off')

    col_labels = ['Bank Group','Actual GNPA\n2024 (%)','Predicted GNPA\n2025 (%)','EWS Signal','Top Driver']
    table_data = []
    cell_colors = []

    signal_color_map = {
        'HIGH ALERT': '#ffcccc',
        'WATCH':      '#fff3cc',
        'ELEVATED':   '#ffe0b2',
        'NORMAL':     '#ccffcc',
    }

    for _, row in dashboard.iterrows():
        sc = signal_color_map.get(row['signal'], '#ffffff')
        table_data.append([
            row['bank_group'],
            f"{row['gnpa_ratio']:.2f}%",
            f"{row['predicted_gnpa_2025']:.2f}%",
            row['signal'],
            row['top_driver']
        ])
        cell_colors.append(['#f8f9fa','#f8f9fa','#f8f9fa', sc,'#f8f9fa'])

    tbl = ax.table(
        cellText   = table_data,
        colLabels  = col_labels,
        cellColours= cell_colors,
        loc        = 'center',
        cellLoc    = 'center'
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(10)
    tbl.scale(1, 2.2)

    # Header styling
    for j in range(len(col_labels)):
        tbl[0,j].set_facecolor('#2c3e50')
        tbl[0,j].set_text_props(color='white', fontweight='bold')

    ax.set_title('RBI NPA Early Warning System — 2025 Outlook\n'
                 'XGBoost prediction | Features: ROA, PCR, GDP, Credit Growth, Repo, CPI\n'
                 'Source: RBI STRBI + author model',
                 fontsize=11, pad=20, y=0.98)

    plt.tight_layout()
    plt.savefig(OUTPUTS + '13_ews_dashboard_table.png',
                dpi=150, bbox_inches='tight')
    plt.close()
    print("  ✅ Saved: 13_ews_dashboard_table.png")


# ============================================================
# CHART 14 — XGBoost Actual vs Predicted (test set)
# ============================================================
print("Generating Chart 14: XGB actual vs predicted...")

fig, ax = plt.subplots(figsize=(9, 7))

for bg in test['bank_group'].unique():
    grp = test[test['bank_group']==bg]
    pos = [test.index.get_loc(i) for i in grp.index]
    ax.scatter(y_test.iloc[pos],
               y_pred_test[pos],
               color=GROUP_COLORS[bg], s=100, alpha=0.85,
               label=bg, zorder=3, edgecolors='white', linewidth=0.5)
    # Year labels
    for j, (_, row) in enumerate(grp.iterrows()):
        p = test.index.get_loc(row.name)
        ax.annotate(str(int(row['year'])),
                    xy=(y_test.iloc[p], y_pred_test[p]),
                    xytext=(4,3), textcoords='offset points',
                    fontsize=7.5, color=GROUP_COLORS[bg])

lims = [min(y_test.min(), y_pred_test.min())-0.3,
        max(y_test.max(), y_pred_test.max())+0.3]
ax.plot(lims, lims, 'k--', linewidth=1, alpha=0.5, label='Perfect prediction')
ax.set_xlim(lims); ax.set_ylim(lims)

ax.set_xlabel('Actual GNPA ratio next year (%)')
ax.set_ylabel('XGBoost predicted GNPA ratio (%)')
ax.set_title(f'XGBoost: actual vs. predicted GNPA ratio (test set 2022–2024)\n'
             f'R² = {r2_test:.3f} | RMSE = {rmse_test:.3f}pp | MAE = {mae_test:.3f}pp',
             fontsize=10, pad=10)
ax.legend(fontsize=9)
plt.tight_layout()
plt.savefig(OUTPUTS + '14_xgb_actual_vs_predicted.png',
            dpi=150, bbox_inches='tight')
plt.close()
print("  ✅ Saved: 14_xgb_actual_vs_predicted.png")


# ============================================================
# PRINT POLICY NOTE NUMBERS
# ============================================================
print("\n" + "="*55)
print("NUMBERS FOR POLICY NOTE + INTERVIEW")
print("="*55)
print(f"""
MODEL PERFORMANCE:
  Train R²:  {r2_train:.3f}
  Test  R²:  {r2_test:.3f}
  Test RMSE: {rmse_test:.3f} percentage points
  Test MAE:  {mae_test:.3f} percentage points

TOP SHAP FEATURE (most important predictor):
  {list(FEAT_LABELS.values())[np.argmax(np.abs(shap_all).mean(axis=0))]}
  Mean |SHAP| = {np.abs(shap_all).mean(axis=0).max():.3f}pp

INTERVIEW LINE:
  "I deliberately chose XGBoost with SHAP over a neural network
  because in a supervisory context, explainability matters more
  than marginal accuracy. A regulator must be able to justify
  why a bank was flagged — 'declining ROA contributed −X pp to
  the stress prediction' is defensible. 'The model said so' is not."

LIMITATION TO STATE:
  "With 32 observations across 4 bank groups, the XGBoost model
  is a pattern-identifier, not a production prediction tool.
  Its primary value is in the SHAP analysis — identifying which
  supervisory indicators correlate most strongly with future NPA,
  and how that varies across bank groups and time periods."
""")

print("="*55)
print("NOTEBOOK 04 COMPLETE")
print("="*55)
print("""
OUTPUTS PRODUCED:
  10_shap_global_importance.png  — mean |SHAP| bar chart
  11_shap_beeswarm.png           — direction + magnitude
  12_shap_force_plots.png        — PSB vs Foreign individual explanations
  13_ews_dashboard_table.png     — traffic light supervisory table
  14_xgb_actual_vs_predicted.png — test set fit
  ews_dashboard_2025.csv         — dashboard data

NEXT → notebook 05: Macro stress test
""")