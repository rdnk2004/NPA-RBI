import sys
import os
sys.path.insert(0, os.path.abspath('src'))

from npa_ews.data import load_bank_level_panel, get_bank_level_model_ready, load_banking_panel
from npa_ews.models.dynamic_panel import DynamicPanelEstimator
from npa_ews import config

print('=== BANK GROUP PANEL (banking_panel.csv) ===')
df_g = load_banking_panel()
print('Bank groups:', df_g['bank_group'].unique())
print('Years:', df_g['year'].min(), 'to', df_g['year'].max())
print('Total rows:', len(df_g))

print('\n=== BANK LEVEL PANEL (bank_level_panel.csv) ===')
df_b = load_bank_level_panel()
print('Banks count:', df_b['bank_clean'].nunique())
print('Bank groups in bank level:', df_b['bank_group'].unique())
print('Years in bank level:', df_b['year'].min(), 'to', df_b['year'].max())
print('Total rows:', len(df_b))

clean_b = get_bank_level_model_ready(df_b)
print('Model ready rows:', len(clean_b))
print('Model ready unique banks:', clean_b['bank_clean'].nunique())

est = DynamicPanelEstimator()
res_dyn = est.fit(clean_b)
print('\n--- Dynamic Panel Results ---')
print(f'N obs: {res_dyn.n_obs}, N entities: {res_dyn.n_entities}')
print(f'Lag persistence (alpha): {res_dyn.lag_persistence:.4f}')
print(f'R-squared within: {res_dyn.r_squared:.4f}')
print('Params and p-values:')
for k, v in res_dyn.params.items():
    print(f'  {k}: coef={v:.4f}, p={res_dyn.pvalues[k]:.4f}')

res_stat = est.fit_static(clean_b)
print('\n--- Static Fixed Effects Results ---')
print(f'N obs: {res_stat.n_obs}, N entities: {res_stat.n_entities}')
print(f'R-squared within: {res_stat.r_squared:.4f}')
for k, v in res_stat.params.items():
    print(f'  {k}: coef={v:.4f}, p={res_stat.pvalues[k]:.4f}')
