import sys, os, re, zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, os.path.abspath("src"))

import numpy as np
import pandas as pd
import docx
from npa_ews import config
from npa_ews.data import (
    load_banking_panel, get_model_ready_frame,
    load_bank_level_panel, get_bank_level_model_ready
)
from npa_ews.models.xgb_model import GnpaXGBModel

print("==========================================================")
print("ADVERSARIAL AUDIT: CODE, DATA, PROSE & CITATIONS")
print("==========================================================")

# 1. Check Dataset Edge Cases & Outliers
df_b = load_bank_level_panel()
clean_b = get_bank_level_model_ready(df_b, features=config.BANK_LEVEL_FEATURES, target="gnpa_next1yr")
clean_b = clean_b.dropna(subset=["pca_breach_next1yr"]).copy()

print("\n[1] RAW vs MODEL-READY COUNTS:")
print(f"Raw bank_level_panel rows: {len(df_b)}, unique banks: {df_b['bank_clean'].nunique()}, years: {df_b['year'].min()}-{df_b['year'].max()}")
print(f"Model-ready rows: {len(clean_b)}, unique banks: {clean_b['bank_clean'].nunique()}, years: {clean_b['year'].min()}-{clean_b['year'].max()}")
print("Year counts in raw df_b (2022-2025):")
print(df_b[df_b["year"] >= 2022]["year"].value_counts().sort_index().to_dict())

print("\n[2] CHECKING EXTREME OUTLIERS IN clean_b:")
for col in ["gnpa_ratio", "gnpa_next1yr", "cd_ratio", "roa", "pcr", "credit_growth_lag2"]:
    top3 = clean_b.nlargest(3, col)[["year", "bank_clean", "bank_group", col]]
    bot2 = clean_b.nsmallest(2, col)[["year", "bank_clean", "bank_group", col]]
    print(f"  {col}: min={clean_b[col].min():.2f}, max={clean_b[col].max():.2f} | top={top3.iloc[0]['bank_clean']} ({top3.iloc[0]['year']}): {top3.iloc[0][col]:.2f}")

# Check sensitivity of Dynamic FE / Static FE to winsorizing or dropping cd_ratio > 500
weird_cd = clean_b[clean_b["cd_ratio"] > 500]
print(f"  Rows with cd_ratio > 500%: {len(weird_cd)} -> {weird_cd[['year', 'bank_clean', 'bank_group', 'cd_ratio']].values.tolist()}")

# 3. Verify 2024 bank-level CRAR / PCR completeness for capital depletion
b2024 = df_b[df_b["year"] == 2024].dropna(subset=["gnpa_ratio", "gross_adv_cr", "crar"]).copy()
missing_pcr_2024 = b2024["pcr"].isna().sum()
print(f"\n[3] 2024 CAPITAL DEPLETION CHECK: n={len(b2024)}, missing PCR={missing_pcr_2024} (filled with 70% fallback in stress.py)")

# 4. Verify Macro Bank-Group ROA SHAP live right now!
df_g = load_banking_panel()
ml_g = get_model_ready_frame(df_g)
xgb_g = GnpaXGBModel().fit(ml_g)
shap_g = xgb_g.global_importance(ml_g)
print("\n[4] LIVE MACRO GROUP SHAP IMPORTANCE (banking_panel.csv, N=40):")
print(shap_g.round(4).to_string())

# 5. Audit All Citations in MD, TEX, DOCX, and Lit Review
print("\n[5] CITATION COMPLETENESS AUDIT:")
with open("papers/IEEE_NPA_EWS_Research_Paper.md", encoding="utf-8") as f:
    md_text = f.read()
body_md, refs_md = md_text.split("## REFERENCES")
cited_md = set(int(m) for m in re.findall(r"\[(\d+)\]", body_md))
listed_md = set(int(m) for m in re.findall(r"^\[(\d+)\]", refs_md, flags=re.M))
print(f"  IEEE MD  -> Cited: {sorted(cited_md)} | Listed: {sorted(listed_md)}")
print(f"  IEEE MD  -> Uncited refs: {sorted(listed_md - cited_md)} | Missing refs: {sorted(cited_md - listed_md)}")

with open("papers/IEEE_NPA_EWS_Research_Paper.tex", encoding="utf-8") as f:
    tex_text = f.read()
body_tex, refs_tex = tex_text.split(r"\begin{thebibliography}")
cited_tex = set()
for grp in re.findall(r"\\cite\{([^}]+)\}", body_tex):
    for k in grp.split(","):
        cited_tex.add(k.strip())
listed_tex = set(re.findall(r"\\bibitem\{([^}]+)\}", refs_tex))
print(f"  IEEE TEX -> Uncited keys: {sorted(listed_tex - cited_tex)} | Missing keys: {sorted(cited_tex - listed_tex)}")

doc_ieee = docx.Document("papers/IEEE_NPA_EWS_Research_Paper.docx")
body_docx_list = []
refs_docx_list = []
in_refs = False
for p in doc_ieee.paragraphs:
    if p.text.strip().startswith("VIII."):
        in_refs = True
        continue
    if in_refs:
        refs_docx_list.append(p.text)
    else:
        body_docx_list.append(p.text)
cited_docx = set(int(m) for m in re.findall(r"\[(\d+)\]", "\n".join(body_docx_list)))
listed_docx = set(int(m) for m in re.findall(r"^\[(\d+)\]", "\n".join(refs_docx_list), flags=re.M))
print(f"  IEEE DOCX -> Uncited refs: {sorted(listed_docx - cited_docx)} | Missing refs: {sorted(cited_docx - listed_docx)}")

# Check Literature Review citations
with open("papers/Literature_Review_and_Research_Gap_Analysis.md", encoding="utf-8") as f:
    lr_text = f.read()
body_lr, refs_lr = lr_text.split("## 6. REFERENCES")
cited_lr = set(int(m) for m in re.findall(r"\[(\d+)\]", body_lr))
listed_lr = set(int(m) for m in re.findall(r"^\[(\d+)\]", refs_lr, flags=re.M))
print(f"  LitRev MD -> Cited: {sorted(cited_lr)} | Uncited refs: {sorted(listed_lr - cited_lr)} | Missing refs: {sorted(cited_lr - listed_lr)}")

# 6. Verify All Reported Confusion Matrices in Table II
print("\n[6] CONFUSION MATRIX EXACT ARITHMETIC CHECK (N=156, P=22):")
reported = [
    ("Naive Persistence", 84.0, 46.2, 81.8, 0.590, 18),
    ("Reg A Logit", 63.5, 23.1, 68.2, 0.345, 15),
    ("Reg A RF", 71.2, 25.5, 54.5, 0.348, 12),
    ("Reg A XGBoost", 76.3, 29.7, 50.0, 0.373, 11),
    ("Reg B Logit", 76.9, 36.0, 81.8, 0.500, 18),
    ("Reg B RF", 80.8, 41.3, 86.4, 0.559, 19),
    ("Reg B XGBoost", 82.1, 42.9, 81.8, 0.562, 18),
]
for name, acc, prec, rec, f1, tp in reported:
    fn = 22 - tp
    # From acc = (TP + TN) / 156 -> TN = round(acc/100 * 156) - TP
    tn = round(acc / 100.0 * 156) - tp
    fp = (156 - 22) - tn
    acc_chk = (tp + tn) / 156 * 100
    prec_chk = tp / (tp + fp) * 100
    rec_chk = tp / 22 * 100
    f1_chk = 2 * tp / (2 * tp + fp + fn)
    ok = (abs(acc_chk - acc) < 0.1 and abs(prec_chk - prec) < 0.1 and abs(rec_chk - rec) < 0.1 and abs(f1_chk - f1) < 0.002)
    print(f"  {name:18s}: TP={tp}, FP={fp}, FN={fn}, TN={tn} -> Acc={acc_chk:.1f}%, Prec={prec_chk:.1f}%, Rec={rec_chk:.1f}%, F1={f1_chk:.3f} | PASS={ok}")
