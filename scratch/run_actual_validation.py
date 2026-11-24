import sys
import os
sys.path.insert(0, os.path.abspath('src'))

import pandas as pd
import numpy as np
from npa_ews.data import load_bank_level_panel, get_bank_level_model_ready, load_banking_panel
from npa_ews.validation import validate_bank_level_models, compare_baselines
from npa_ews.models.dynamic_panel import DynamicPanelEstimator
from npa_ews import config

print('=== 1. RUNNING BANK-LEVEL VALIDATION (REGRESSION & CLASSIFICATION) ===')
df_b = load_bank_level_panel()
val_res = validate_bank_level_models(df_b, split_year=2021)
print(f"Train obs (<=2021): {val_res['n_train']}, Test obs (>=2022): {val_res['n_test']}")

print('\n--- Bank Level Continuous Regression ---')
print(val_res['regression'])

print('\n--- Bank Level PCA Breach Classification (Proxy GNPA >= 6.0%) ---')
print(val_res['classification'])

print('\n=== 2. RUNNING BANK-GROUP BASELINE COMPARISON ===')
from npa_ews.data import get_model_ready_frame
df_g = load_banking_panel()
ml_g = get_model_ready_frame(df_g)
base_res = compare_baselines(ml_g)
print(base_res)
