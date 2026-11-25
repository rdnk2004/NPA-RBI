import sys, os
sys.path.insert(0, os.path.abspath('src'))

import pandas as pd
from npa_ews.data import load_bank_level_panel, get_bank_level_model_ready

df_b = load_bank_level_panel()
clean_b = get_bank_level_model_ready(df_b)

# Check banks appearing in multiple bank_groups
bg_counts = clean_b.groupby("bank_clean")["bank_group"].nunique()
multi = bg_counts[bg_counts > 1]
print("Banks with multiple bank_groups in clean_b:", len(multi))
for b in multi.index:
    print(f"  {b}: {clean_b[clean_b['bank_clean']==b][['year','bank_group']].values.tolist()}")

# Check what bank_group years look like in clean_b
print("\nYears in clean_b:", sorted(clean_b["year"].unique()))
print("Sample train (<=2021) vs test (>=2022) counts:")
print("  Train:", len(clean_b[clean_b["year"] <= 2021]), "Test:", len(clean_b[clean_b["year"] >= 2022]))
print("  Test positives (pca_breach_next1yr==1):", int(clean_b[clean_b["year"] >= 2022]["pca_breach_next1yr"].sum()))
