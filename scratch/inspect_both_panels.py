import sys, os
sys.path.insert(0, os.path.abspath('src'))

import pandas as pd
import numpy as np
from npa_ews.data import (
    load_banking_panel, get_model_ready_frame, group_reliability,
    load_bank_level_panel, get_bank_level_model_ready
)
from npa_ews import config

print("=== 1. BANK-GROUP PANEL (banking_panel.csv) ===")
df_g = load_banking_panel()
ml_g = get_model_ready_frame(df_g)
print("Total rows:", len(df_g), "Model-ready rows:", len(ml_g))
print(group_reliability(ml_g))
print("\nYear ranges per group in banking_panel.csv (raw vs model_ready):")
for bg in df_g["bank_group"].unique():
    sub_raw = df_g[df_g["bank_group"] == bg]
    sub_ml = ml_g[ml_g["bank_group"] == bg]
    print(f"  {bg}: raw n={len(sub_raw)} ({sub_raw['year'].min()}-{sub_raw['year'].max()}), ml n={len(sub_ml)} ({sub_ml['year'].min() if len(sub_ml) else 'NA'}-{sub_ml['year'].max() if len(sub_ml) else 'NA'})")

print("\n=== 2. BANK-LEVEL PANEL (bank_level_panel.csv) ===")
df_b = load_bank_level_panel()
clean_b = get_bank_level_model_ready(df_b)
print(f"Raw shape: {df_b.shape}, unique bank_clean: {df_b['bank_clean'].nunique()}, years: {df_b['year'].min()}-{df_b['year'].max()}")
print(f"Model-ready shape: {clean_b.shape}, unique bank_clean: {clean_b['bank_clean'].nunique()}, years: {clean_b['year'].min()}-{clean_b['year'].max()}")
print("\nModel-ready counts by bank_group:")
print(clean_b.groupby("bank_group").agg(obs=("year", "count"), banks=("bank_clean", "nunique"), yr_min=("year", "min"), yr_max=("year", "max")))

print("\nChecking for aggregate rows inside bank_level_panel.csv:")
agg_suspects = [b for b in df_b["bank_clean"].unique() if any(k in b for k in ["BANKS", "TOTAL", "SCHEDULED", "ALL "])]
print("Suspect aggregate names in raw:", agg_suspects)
agg_clean = [b for b in clean_b["bank_clean"].unique() if any(k in b for k in ["BANKS", "TOTAL", "SCHEDULED", "ALL "])]
print("Suspect aggregate names in clean:", agg_clean)

print("\nChecking 2024 latest bank-level cross section:")
b2024 = df_b[df_b["year"] == 2024]
print("2024 raw banks:", len(b2024), "by group:", b2024["bank_group"].value_counts().to_dict())
print("2024 PSB names:", b2024[b2024["bank_group"] == "PSB"]["bank_clean"].tolist())
print("Pre-2017 SBI associates in clean_b:", [b for b in clean_b["bank_clean"].unique() if "STATE BANK" in b])
