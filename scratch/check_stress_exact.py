import sys, os
sys.path.insert(0, os.path.abspath('src'))

import numpy as np
import pandas as pd
from npa_ews.data import load_banking_panel, get_model_ready_frame, group_reliability, load_bank_level_panel
from npa_ews.models.panel_fe import FixedEffectsRegressor
from npa_ews.stress import run_stress_test, bootstrap_stress_test, simulate_bank_capital_depletion
from npa_ews import config

df_g = load_banking_panel()
ml_g = get_model_ready_frame(df_g)
print("=== GROUP RELIABILITY IN RESTORED BANKING_PANEL.CSV ===")
print(group_reliability(ml_g))

fe_g = FixedEffectsRegressor().fit(ml_g)
print("\nFE Bank-Group Coefficients (N =", fe_g.n_obs, ", within R2 =", round(fe_g.r_squared, 3), "):")
for k, v in fe_g.coefficients.items():
    print(f"  {k:20s}: coef={v:.4f}")

latest_g = df_g[df_g["year"] == 2024].set_index("bank_group")
st_df = run_stress_test(fe_g, latest_g)
print("\n=== POINT ESTIMATES (run_stress_test) ===")
print(st_df.to_string())

boot = bootstrap_stress_test(ml_g, latest_g, n_boot=1000)
print("\n=== BOOTSTRAP KEYS ===")
for k, v in boot.items():
    print(f"\nScenario: {repr(k)}")
    print(v)

# Also check bank-level capital depletion in 2024 under Tail Risk shock!
df_b = load_bank_level_panel()
b2024 = df_b[df_b["year"] == 2024].dropna(subset=["gnpa_ratio", "gross_adv_cr", "crar"]).copy()
print("\n=== 2024 BANK-LEVEL CROSS SECTION SUMMARY ===")
print("Banks with CRAR & GNPA in 2024:", len(b2024), "by group:", b2024["bank_group"].value_counts().to_dict())
# Apply Tail risk gnpa_increase from FE (Tail Risk - Baseline)
tail_col = st_df.columns[-1]
base_col = st_df.columns[0]
gnpa_shock_pp = float(st_df.loc["PSB", tail_col] - st_df.loc["PSB", base_col])
print(f"FE Tail Risk systemic GNPA shock (pp): {gnpa_shock_pp:.3f}")
cap_dep = simulate_bank_capital_depletion(b2024, gnpa_increase_pct=gnpa_shock_pp)
print(cap_dep.groupby("bank_group")[["gnpa_ratio", "stressed_gnpa", "crar", "stressed_crar", "crar_depletion_pp", "crar_breach_9pct"]].agg({
    "gnpa_ratio": "mean",
    "stressed_gnpa": "mean",
    "crar": "mean",
    "stressed_crar": "mean",
    "crar_depletion_pp": "mean",
    "crar_breach_9pct": "sum"
}).round(2))
