# ============================================================
# NOTEBOOK 02 — EXPLORATORY DATA ANALYSIS (EDA)
# RBI NPA Early Warning System
# Run from NPA/ root:  python notebooks/02_eda.py
# Outputs go to:       outputs/
# ============================================================

import sys
import pandas as pd
# pyrefly: ignore [missing-import]
import numpy as np
# pyrefly: ignore [missing-import]
import matplotlib.pyplot as plt
# pyrefly: ignore [missing-import]
import matplotlib.ticker as mticker
# pyrefly: ignore [missing-import]
import matplotlib.patches as mpatches
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Force stdout/stderr to use UTF-8 encoding on Windows to prevent UnicodeEncodeError
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

DATA    = "../datasets/"
OUTPUTS = "../outputs/"

# ── Global style ─────────────────────────────────────────────
plt.rcParams.update({
    'figure.dpi':       150,
    'font.family':      'DejaVu Sans',
    'font.size':        10,
    'axes.spines.top':  False,
    'axes.spines.right':False,
    'axes.grid':        True,
    'grid.alpha':       0.2,
    'grid.linestyle':   '--',
})

GROUP_COLORS = {
    'PSB':     '#e74c3c',
    'Private': '#3498db',
    'Foreign': '#27ae60',
    'SFB':     '#f39c12',
}

# ── Load data ─────────────────────────────────────────────────
panel = pd.read_csv(DATA + "banking_panel.csv")
macro = pd.read_csv(DATA + "macro_annual.csv")

# Fix: drop future years
panel = panel[panel['year'] <= 2025].copy()
macro = macro[macro['year'] <= 2025].copy()

print(f"Panel loaded: {panel.shape} | Years: {panel['year'].min()}–{panel['year'].max()}")
print(f"Macro loaded: {macro.shape}")


# ============================================================
# CHART 1 — GNPA RATIO BY BANK GROUP (THE BIG PICTURE)
# ============================================================
print("\nGenerating Chart 1: GNPA cycle...")

fig, ax = plt.subplots(figsize=(14, 6))

for bg, grp in panel.groupby('bank_group'):
    grp_valid = grp.dropna(subset=['gnpa_ratio']).sort_values('year')
    ax.plot(grp_valid['year'], grp_valid['gnpa_ratio'],
            marker='o', linewidth=2.5, markersize=5,
            color=GROUP_COLORS[bg], label=bg, zorder=3)

# Event markers
events = {
    2016: ('AQR\n(2016)', '#8e44ad'),
    2019: ('IL&FS\n(2019)', '#e67e22'),
    2020: ('COVID\n(2020)', '#c0392b'),
    2022: ('IBC\nresolution', '#16a085'),
}
ymax = panel['gnpa_ratio'].max()
for yr, (label, color) in events.items():
    ax.axvline(yr, color=color, linestyle='--', linewidth=1, alpha=0.6)
    ax.text(yr + 0.1, ymax * 0.88, label,
            fontsize=8, color=color,
            bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7))

ax.axhline(7.0,  color='red',    linestyle=':',  linewidth=1.2, alpha=0.7,
           label='PCA threshold (7%)')
ax.axhline(10.0, color='darkred',linestyle=':',  linewidth=1,   alpha=0.5,
           label='Severe stress (10%)')

ax.set_title('GNPA ratio by bank group (2004–2025): India NPA cycle\n'
             'Source: RBI Statistical Tables Relating to Banks in India',
             fontsize=11, pad=10)
ax.set_ylabel('GNPA Ratio (%)')
ax.set_xlabel('Year (March end)')
ax.legend(fontsize=9, loc='upper left')
ax.set_xlim(2003, 2026)
plt.tight_layout()
plt.savefig(OUTPUTS + '01_npa_cycle_bank_groups.png',
            dpi=150, bbox_inches='tight')
plt.close()
print("  ✅ Saved: 01_npa_cycle_bank_groups.png")


# ============================================================
# CHART 2 — CREDIT BOOM → NPA CRISIS (PSB + PRIVATE)
# Dual axis: credit growth bars + GNPA line
# ============================================================
print("Generating Chart 2: Credit growth vs NPA...")

fig, axes = plt.subplots(1, 2, figsize=(15, 6))

for ax, bg, title_extra in zip(
    axes,
    ['Private', 'PSB'],
    ['(full history 2004–2025)', '(post-merger data 2018–2025)']
):
    grp = panel[panel['bank_group'] == bg].dropna(
        subset=['gnpa_ratio','credit_growth']).sort_values('year')

    ax2 = ax.twinx()

    bars = ax.bar(grp['year'], grp['credit_growth'],
                  alpha=0.55, color=GROUP_COLORS[bg],
                  width=0.6, label='Credit growth %')
    ax.set_ylabel('Credit Growth (% YoY)', color=GROUP_COLORS[bg])
    ax.tick_params(axis='y', labelcolor=GROUP_COLORS[bg])
    ax.axhline(0, color='black', linewidth=0.5)

    ax2.plot(grp['year'], grp['gnpa_ratio'],
             color='#2c3e50', linewidth=2.5,
             marker='s', markersize=5, label='GNPA ratio %')
    ax2.set_ylabel('GNPA Ratio (%)', color='#2c3e50')
    ax2.tick_params(axis='y', labelcolor='#2c3e50')

    ax.set_title(f'{bg} Banks: Credit growth vs GNPA ratio\n{title_extra}',
                 fontsize=10)
    ax.set_xlabel('Year')

    # Combined legend
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1+h2, l1+l2, fontsize=8, loc='upper left')

plt.suptitle('Credit boom precedes NPA stress: evidence from Indian banking\n'
             'Source: RBI STRBI + author calculations',
             fontsize=11, y=1.01)
plt.tight_layout()
plt.savefig(OUTPUTS + '02_credit_growth_vs_npa.png',
            dpi=150, bbox_inches='tight')
plt.close()
print("  ✅ Saved: 02_credit_growth_vs_npa.png")


# ============================================================
# CHART 3 — PSB 3-PANEL SUPERVISORY SIGNAL CHART
# Panel 1: GNPA ratio  |  Panel 2: CAR (ROA proxy)  |  Panel 3: PCR
# ============================================================
print("Generating Chart 3: PSB supervisory signals...")

psb = panel[panel['bank_group'] == 'PSB'].sort_values('year')

fig, axes = plt.subplots(3, 1, figsize=(13, 11), sharex=True)

# Panel 1: GNPA
axes[0].fill_between(psb['year'], psb['gnpa_ratio'],
                     alpha=0.2, color='#e74c3c')
axes[0].plot(psb['year'], psb['gnpa_ratio'],
             color='#e74c3c', linewidth=2.5, marker='o', markersize=5)
axes[0].axhline(7.0,  color='red',    linestyle=':', linewidth=1.2,
                label='PCA RT1 (7%)')
axes[0].axhline(10.0, color='darkred',linestyle=':', linewidth=1,
                label='PCA RT2 (10%)')
axes[0].set_ylabel('GNPA Ratio (%)')
axes[0].set_title('PSB supervisory early warning signals (2018–2025)\n'
                  'Declining ROA and PCR precede GNPA spike',
                  fontsize=11)
axes[0].legend(fontsize=8)

# Panel 2: ROA
axes[1].plot(psb['year'], psb['roa'],
             color='#3498db', linewidth=2.5, marker='s', markersize=5)
axes[1].fill_between(psb['year'], psb['roa'], 0,
                     where=(psb['roa'] < 0),
                     alpha=0.3, color='red', label='Negative ROA (loss)')
axes[1].axhline(0,    color='red',   linestyle='-',  linewidth=0.8)
axes[1].axhline(0.25, color='orange',linestyle=':',  linewidth=1.2,
                label='PCA trigger (ROA < 0.25%)')
axes[1].set_ylabel('Return on Assets (%)')
axes[1].legend(fontsize=8)

# Panel 3: PCR
axes[2].plot(psb['year'], psb['pcr'],
             color='#27ae60', linewidth=2.5, marker='^', markersize=5)
axes[2].fill_between(psb['year'], psb['pcr'],
                     alpha=0.15, color='#27ae60')
axes[2].axhline(70, color='green', linestyle=':', linewidth=1.2,
                label='Healthy PCR (>70%)')
axes[2].set_ylabel('Provision Coverage Ratio (%)')
axes[2].set_xlabel('Year (March end)')
axes[2].legend(fontsize=8)

for ax in axes:
    ax.set_xlim(2017.5, 2025.5)

plt.tight_layout()
plt.savefig(OUTPUTS + '03_psb_supervisory_signals.png',
            dpi=150, bbox_inches='tight')
plt.close()
print("  ✅ Saved: 03_psb_supervisory_signals.png")


# ============================================================
# CHART 4 — CORRELATION MATRIX
# ============================================================
print("Generating Chart 4: Correlation matrix...")

feature_cols = [
    'gnpa_ratio', 'credit_growth', 'credit_growth_lag1',
    'credit_growth_lag2', 'roa', 'pcr',
    'gdp_growth', 'repo_rate', 'iip_avg', 'cpi_avg'
]

corr_df = panel[feature_cols].dropna().corr()

# Readable labels
labels = {
    'gnpa_ratio':          'GNPA Ratio',
    'credit_growth':       'Credit Growth',
    'credit_growth_lag1':  'Credit Growth (t-1)',
    'credit_growth_lag2':  'Credit Growth (t-2)',
    'roa':                 'ROA',
    'pcr':                 'PCR',
    'gdp_growth':          'GDP Growth',
    'repo_rate':           'Repo Rate',
    'iip_avg':             'IIP Growth',
    'cpi_avg':             'CPI Inflation',
}
corr_df = corr_df.rename(index=labels, columns=labels)

fig, ax = plt.subplots(figsize=(11, 9))
mask = np.triu(np.ones_like(corr_df, dtype=bool))
sns.heatmap(corr_df, mask=mask,
            annot=True, fmt='.2f',
            cmap='RdBu_r', center=0, vmin=-1, vmax=1,
            linewidths=0.3, ax=ax,
            cbar_kws={'label': 'Pearson correlation', 'shrink': 0.8})
ax.set_title('Correlation matrix: banking indicators vs. GNPA ratio\n'
             'Red = amplifies NPA stress | Blue = buffers NPA stress',
             fontsize=11, pad=10)
plt.tight_layout()
plt.savefig(OUTPUTS + '04_correlation_matrix.png',
            dpi=150, bbox_inches='tight')
plt.close()
print("  ✅ Saved: 04_correlation_matrix.png")


# ============================================================
# CHART 5 — ALL BANK GROUPS: GNPA vs GDP GROWTH SCATTER
# Colour = bank group, size = year (bigger = more recent)
# ============================================================
print("Generating Chart 5: GNPA vs GDP growth scatter...")

plot_df = panel.dropna(subset=['gnpa_ratio','gdp_growth']).copy()
# Size: scale year to marker size
yr_min, yr_max = plot_df['year'].min(), plot_df['year'].max()
plot_df['msize'] = 40 + 120 * (plot_df['year'] - yr_min) / (yr_max - yr_min)

fig, ax = plt.subplots(figsize=(11, 7))

for bg, grp in plot_df.groupby('bank_group'):
    ax.scatter(grp['gdp_growth'], grp['gnpa_ratio'],
               s=grp['msize'], color=GROUP_COLORS[bg],
               alpha=0.75, label=bg, zorder=3, edgecolors='white', linewidth=0.5)
    # Annotate a few key years
    for _, row in grp[grp['year'].isin([2018,2021,2025])].iterrows():
        ax.annotate(str(int(row['year'])),
                    xy=(row['gdp_growth'], row['gnpa_ratio']),
                    xytext=(4, 2), textcoords='offset points',
                    fontsize=7, color=GROUP_COLORS[bg])

# Quadrant lines
ax.axvline(5.0, color='grey', linestyle='--', linewidth=0.8, alpha=0.5)
ax.axhline(7.0, color='red',  linestyle='--', linewidth=0.8, alpha=0.5,
           label='PCA threshold (7%)')

ax.set_xlabel('GDP Growth (%)', fontsize=11)
ax.set_ylabel('GNPA Ratio (%)', fontsize=11)
ax.set_title('GNPA ratio vs. GDP growth by bank group\n'
             'Larger circles = more recent years | '
             'Low GDP + High NPA = stress quadrant (top-left)',
             fontsize=10)
ax.legend(fontsize=9)
plt.tight_layout()
plt.savefig(OUTPUTS + '05_gnpa_vs_gdp_scatter.png',
            dpi=150, bbox_inches='tight')
plt.close()
print("  ✅ Saved: 05_gnpa_vs_gdp_scatter.png")


# ============================================================
# CHART 6 — PCR ACROSS ALL GROUPS (buffer strength)
# ============================================================
print("Generating Chart 6: PCR across groups...")

pcr_df = panel.dropna(subset=['pcr']).sort_values('year')

fig, ax = plt.subplots(figsize=(13, 6))

for bg, grp in pcr_df.groupby('bank_group'):
    grp = grp.sort_values('year')
    ax.plot(grp['year'], grp['pcr'],
            marker='o', linewidth=2, markersize=5,
            color=GROUP_COLORS[bg], label=bg)

ax.axhline(70, color='green',  linestyle=':', linewidth=1.2,
           label='Healthy buffer (>70%)')
ax.axhline(50, color='orange', linestyle=':', linewidth=1,
           label='Weak buffer (<50%)')

ax.set_title('Provision Coverage Ratio (PCR) by bank group (2018–2025)\n'
             'PCR = (Gross NPA − Net NPA) / Gross NPA × 100\n'
             'Source: RBI STRBI Table 6 — author calculations',
             fontsize=10)
ax.set_ylabel('PCR (%)')
ax.set_xlabel('Year (March end)')
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{int(x)}'))
ax.legend(fontsize=9)
plt.tight_layout()
plt.savefig(OUTPUTS + '06_pcr_all_groups.png',
            dpi=150, bbox_inches='tight')
plt.close()
print("  ✅ Saved: 06_pcr_all_groups.png")


# ============================================================
# PRINT KEY FINDINGS FOR POLICY NOTE
# ============================================================
print("\n" + "=" * 55)
print("KEY FINDINGS — use these in your policy note")
print("=" * 55)

# 1. Peak GNPA
peak = panel.loc[panel['gnpa_ratio'].idxmax()]
print(f"\n1. Peak GNPA: {peak['bank_group']} in {int(peak['year'])} "
      f"at {peak['gnpa_ratio']:.1f}%")

# 2. PSB ROA negative years
psb_neg_roa = panel[(panel['bank_group']=='PSB') & (panel['roa'] < 0)]
print(f"\n2. PSB negative ROA years: {sorted(psb_neg_roa['year'].tolist())}")

# 3. Correlation of credit_growth_lag2 with gnpa_ratio
valid = panel[['gnpa_ratio','credit_growth_lag2']].dropna()
corr_val = valid['gnpa_ratio'].corr(valid['credit_growth_lag2'])
print(f"\n3. Correlation(GNPA ratio, credit_growth_lag2): {corr_val:.3f}")

# 4. Correlation of GDP growth with gnpa_ratio
valid2 = panel[['gnpa_ratio','gdp_growth']].dropna()
corr_gdp = valid2['gnpa_ratio'].corr(valid2['gdp_growth'])
print(f"\n4. Correlation(GNPA ratio, GDP growth): {corr_gdp:.3f}")

# 5. PCR improvement PSB
psb_pcr = panel[panel['bank_group']=='PSB'].sort_values('year')
pcr_2018 = psb_pcr[psb_pcr['year']==2018]['pcr'].values
pcr_2025 = psb_pcr[psb_pcr['year']==2025]['pcr'].values
if len(pcr_2018) and len(pcr_2025):
    print(f"\n5. PSB PCR: {pcr_2018[0]:.1f}% (2018) → {pcr_2025[0]:.1f}% (2025) "
          f"[+{pcr_2025[0]-pcr_2018[0]:.1f}pp improvement]")

# 6. Stress events
stress = panel[panel['stress_next1yr']==1][['year','bank_group','gnpa_ratio']]
print(f"\n6. Stress events detected (GNPA crossing 7% next year):")
print(stress.to_string(index=False))

print("\n" + "=" * 55)
print("NOTEBOOK 02 COMPLETE — 6 charts saved to outputs/")
print("=" * 55)
print("""
CHARTS PRODUCED:
  01_npa_cycle_bank_groups.png   — headline chart
  02_credit_growth_vs_npa.png    — leading indicator visual
  03_psb_supervisory_signals.png — 3-panel EWS signal chart
  04_correlation_matrix.png      — feature selection foundation
  05_gnpa_vs_gdp_scatter.png     — macro-NPA relationship
  06_pcr_all_groups.png          — buffer strength chart

NEXT → notebook 03: Panel regression with fixed effects
""")