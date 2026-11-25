"""
Data Builder for NPA Early Warning System.

Reconstructs:
1. Macro Bank-Group Panel (banking_panel.csv): Restores uninterrupted 2004-2025 series
   for Public Sector Banks (PSB) by correctly aggregating 'STATE BANK OF INDIA AND ITS ASSOCIATES'
   and 'NATIONALISED BANKS' prior to the 2018 reporting consolidation.
2. Granular Bank-Level Longitudinal Panel (bank_level_panel.csv): Extracts longitudinal micro-panel
   of 40+ scheduled commercial banks from 2005 to 2025 merging GNPA, Advances, RoA, CRAR,
   CD ratio, PCR, and macroeconomic variables.
"""
from __future__ import annotations

import logging
import re
from pathlib import Path
import numpy as np
import openpyxl
import pandas as pd

from npa_ews import config

logger = logging.getLogger(__name__)

def _clean_bank_name(name: str) -> str:
    """Normalize bank names across different RBI reporting tables."""
    if not name:
        return ""
    n = str(name).strip().upper()
    n = re.sub(r"\s+", " ", n)
    n = n.replace(".", "").replace(",", "").replace("-", " ")
    n = re.sub(r"\bLIMITED\b", "LTD", n)
    n = re.sub(r"\bPUBLIC COMPANY LTD\b", "LTD", n)
    n = re.sub(r"\bNATIONAL ASSOCIATION\b", "NA", n)
    n = re.sub(r"\bCORPN\b", "CORP", n)
    return n.strip()

def build_macro_banking_panel(
    data_dir: Path = config.DATA_DIR,
    save: bool = True
) -> pd.DataFrame:
    """Extract and reconstruct the bank-group macro panel with full historical PSB series."""
    gnpa_file = data_dir / "F4_GNPA.xlsx"
    roa_file = data_dir / "F6_T10.xlsx"
    movement_file = data_dir / "F7_NPA_MOVEMENT.xlsx"
    macro_file = data_dir / "macro_annual.csv"

    wb = openpyxl.load_workbook(gnpa_file, read_only=True, data_only=True)
    ws = wb["Report 1"]
    
    current_year = None
    records = []
    
    for row in ws.iter_rows(values_only=True):
        if row[1] and str(row[1]).strip().isdigit():
            current_year = int(str(row[1]).strip())
        bank = str(row[2]).strip() if len(row) > 2 and row[2] else ""
        if not current_year or not bank:
            continue
            
        def to_float(val):
            if val is None or str(val).strip() in ["-", "..", "", "NA"]:
                return np.nan
            try:
                return float(val)
            except:
                return np.nan

        gnpa = to_float(row[3])
        adv = to_float(row[4])
        
        # Capture raw group totals
        if bank in [
            "STATE BANK OF INDIA AND ITS ASSOCIATES",
            "NATIONALISED BANKS",
            "PUBLIC SECTOR BANKS",
            "PRIVATE SECTOR BANKS",
            "FOREIGN BANKS",
            "SMALL FINANCE BANKS"
        ]:
            records.append({
                "year": current_year,
                "raw_group": bank,
                "gross_npa_cr": gnpa,
                "gross_adv_cr": adv
            })
    wb.close()

    raw_df = pd.DataFrame(records)
    
    # Process Public Sector Banks:
    # Before 2018: SBI & Assoc + Nationalised Banks = PSB
    # 2018+: PUBLIC SECTOR BANKS
    psb_pre2018 = (
        raw_df[raw_df["raw_group"].isin(["STATE BANK OF INDIA AND ITS ASSOCIATES", "NATIONALISED BANKS"])]
        .groupby("year")[["gross_npa_cr", "gross_adv_cr"]]
        .sum(min_count=1)
        .reset_index()
    )
    psb_pre2018["bank_group"] = "PSB"
    
    psb_post2018 = raw_df[raw_df["raw_group"] == "PUBLIC SECTOR BANKS"].copy()
    psb_post2018["bank_group"] = "PSB"
    
    psb_combined = pd.concat([psb_pre2018[psb_pre2018["year"] < 2018], psb_post2018], ignore_index=True)
    
    # Process other groups
    pvt = raw_df[raw_df["raw_group"] == "PRIVATE SECTOR BANKS"].copy()
    pvt["bank_group"] = "Private"
    
    foreign = raw_df[raw_df["raw_group"] == "FOREIGN BANKS"].copy()
    foreign["bank_group"] = "Foreign"
    
    sfb = raw_df[raw_df["raw_group"] == "SMALL FINANCE BANKS"].copy()
    sfb["bank_group"] = "SFB"
    
    gnpa_df = pd.concat([psb_combined, pvt, foreign, sfb], ignore_index=True)
    gnpa_df = gnpa_df[["year", "bank_group", "gross_npa_cr", "gross_adv_cr"]].dropna(subset=["gross_adv_cr"])
    gnpa_df = gnpa_df.sort_values(["bank_group", "year"]).reset_index(drop=True)
    
    gnpa_df["gnpa_ratio"] = (gnpa_df["gross_npa_cr"] / gnpa_df["gross_adv_cr"]) * 100
    gnpa_df["credit_growth"] = gnpa_df.groupby("bank_group")["gross_adv_cr"].pct_change() * 100
    gnpa_df["credit_growth_lag1"] = gnpa_df.groupby("bank_group")["credit_growth"].shift(1)
    gnpa_df["credit_growth_lag2"] = gnpa_df.groupby("bank_group")["credit_growth"].shift(2)
    gnpa_df["credit_growth_3y_avg"] = (
        gnpa_df.groupby("bank_group")["credit_growth"].rolling(3, min_periods=2).mean().reset_index(drop=True)
    )
    gnpa_df["gnpa_next1yr"] = gnpa_df.groupby("bank_group")["gnpa_ratio"].shift(-1)
    gnpa_df["gnpa_next2yr"] = gnpa_df.groupby("bank_group")["gnpa_ratio"].shift(-2)
    gnpa_df["stress_next1yr"] = (gnpa_df["gnpa_next1yr"] >= 6.0).astype(float)
    gnpa_df["stress_next2yr"] = (gnpa_df["gnpa_next2yr"] >= 6.0).astype(float)

    # Extract ROA from F6_T10.xlsx
    wb2 = openpyxl.load_workbook(roa_file, read_only=True, data_only=True)
    ws2 = wb2["Report 1"]
    roa_records = []
    current_yr = None
    for row in ws2.iter_rows(values_only=True):
        yr_raw = str(row[2]).strip() if len(row) > 2 and row[2] else ""
        if "-" in yr_raw and len(yr_raw) == 7 and yr_raw[:4].isdigit():
            current_yr = int(yr_raw[:4]) + 1
        if len(row) > 3 and row[3] and "Return on assets" in str(row[3]) and current_yr:
            def roa_val(v):
                if v is None or str(v).strip() in ["-", "", "..", " "]:
                    return np.nan
                try:
                    return float(v)
                except:
                    return np.nan
            roa_records.append({
                "year": current_yr,
                "PSB": roa_val(row[6]),
                "Private": roa_val(row[7]),
                "Foreign": roa_val(row[8]),
                "SFB": roa_val(row[9]),
            })
    wb2.close()
    
    roa_df = pd.DataFrame(roa_records).drop_duplicates(subset="year")
    roa_long = roa_df.melt(id_vars="year", var_name="bank_group", value_name="roa")
    
    # Extract PCR from F7_NPA_MOVEMENT.xlsx
    wb3 = openpyxl.load_workbook(movement_file, read_only=True, data_only=True)
    ws3 = wb3["Report 1"]
    pcr_records = []
    curr_yr = None
    for row in ws3.iter_rows(values_only=True):
        if row[1] and str(row[1]).strip().isdigit():
            curr_yr = int(str(row[1]).strip())
        b = str(row[2]).strip() if len(row) > 2 and row[2] else ""
        if not curr_yr or not b:
            continue
        def parse_f(v):
            if v is None or str(v).strip() in ["-", "..", ""]:
                return np.nan
            try:
                return float(v)
            except:
                return np.nan
        # col 7 = closing gross npa, col 9 = closing net npa
        if b in [
            "STATE BANK OF INDIA AND ITS ASSOCIATES", "NATIONALISED BANKS",
            "PUBLIC SECTOR BANKS", "PRIVATE SECTOR BANKS", "FOREIGN BANKS", "SMALL FINANCE BANKS"
        ]:
            gnpa_close = parse_f(row[7])
            nnpa_close = parse_f(row[9])
            pcr_records.append({
                "year": curr_yr,
                "raw_group": b,
                "gross_npa_close": gnpa_close,
                "net_npa_close": nnpa_close
            })
    wb3.close()
    
    pcr_raw = pd.DataFrame(pcr_records)
    psb_pcr_pre = (
        pcr_raw[pcr_raw["raw_group"].isin(["STATE BANK OF INDIA AND ITS ASSOCIATES", "NATIONALISED BANKS"])]
        .groupby("year")[["gross_npa_close", "net_npa_close"]].sum(min_count=1).reset_index()
    )
    psb_pcr_pre["bank_group"] = "PSB"
    psb_pcr_post = pcr_raw[pcr_raw["raw_group"] == "PUBLIC SECTOR BANKS"].copy()
    psb_pcr_post["bank_group"] = "PSB"
    psb_pcr = pd.concat([psb_pcr_pre[psb_pcr_pre["year"] < 2018], psb_pcr_post], ignore_index=True)
    
    pvt_pcr = pcr_raw[pcr_raw["raw_group"] == "PRIVATE SECTOR BANKS"].copy()
    pvt_pcr["bank_group"] = "Private"
    foreign_pcr = pcr_raw[pcr_raw["raw_group"] == "FOREIGN BANKS"].copy()
    foreign_pcr["bank_group"] = "Foreign"
    sfb_pcr = pcr_raw[pcr_raw["raw_group"] == "SMALL FINANCE BANKS"].copy()
    sfb_pcr["bank_group"] = "SFB"
    
    pcr_all = pd.concat([psb_pcr, pvt_pcr, foreign_pcr, sfb_pcr], ignore_index=True)
    pcr_all["net_npa_cr"] = pcr_all["net_npa_close"]
    pcr_all["pcr"] = (1 - (pcr_all["net_npa_close"] / pcr_all["gross_npa_close"])) * 100
    pcr_clean = pcr_all[["year", "bank_group", "net_npa_cr", "pcr"]].dropna(subset=["pcr"])

    # Load Macro
    macro_df = pd.read_csv(macro_file)
    
    # Merge all
    panel = pd.merge(gnpa_df, roa_long, on=["year", "bank_group"], how="left")
    panel = pd.merge(panel, pcr_clean, on=["year", "bank_group"], how="left")
    panel = pd.merge(panel, macro_df, on="year", how="left")
    
    cols_order = [
        "year", "bank_group", "gross_npa_cr", "gross_adv_cr", "gnpa_ratio",
        "credit_growth", "roa", "repo_rate", "cpi_avg", "iip_avg", "gdp_growth",
        "credit_growth_lag1", "credit_growth_lag2", "credit_growth_3y_avg",
        "gnpa_next1yr", "gnpa_next2yr", "stress_next1yr", "stress_next2yr",
        "net_npa_cr", "pcr"
    ]
    panel = panel[cols_order].sort_values(["bank_group", "year"]).reset_index(drop=True)
    
    if save:
        out_csv = data_dir / "banking_panel.csv"
        panel.to_csv(out_csv, index=False)
        logger.info("Saved restored macro panel to %s (%d rows)", out_csv, len(panel))
        
    return panel

def build_bank_level_panel(
    data_dir: Path = config.DATA_DIR,
    save: bool = True
) -> pd.DataFrame:
    """Extract and build longitudinal bank-level panel (2005-2025)."""
    gnpa_file = data_dir / "F4_GNPA.xlsx"
    ratios_file = data_dir / "F5_T11.xlsx"
    movement_file = data_dir / "F7_NPA_MOVEMENT.xlsx"
    macro_file = data_dir / "macro_annual.csv"

    # Step 1: Read F4_GNPA bank rows
    wb = openpyxl.load_workbook(gnpa_file, read_only=True, data_only=True)
    ws = wb["Report 1"]
    
    bank_records = []
    current_year = None
    current_section = "PSB"  # In F4, year starts with SBI/PSB
    
    for row in ws.iter_rows(values_only=True):
        if row[1] and str(row[1]).strip().isdigit():
            current_year = int(str(row[1]).strip())
            current_section = "PSB"
        bank_raw = str(row[2]).strip() if len(row) > 2 and row[2] else ""
        if not current_year or not bank_raw:
            continue
            
        b_upper = bank_raw.upper()
        if b_upper == "STATE BANK OF INDIA AND ITS ASSOCIATES":
            # Subtotal row; Nationalised Banks (also PSB) appear immediately below
            continue
        elif b_upper in ["NATIONALISED BANKS", "PUBLIC SECTOR BANKS"]:
            current_section = "Private"  # Next section is Private
            continue
        elif b_upper == "PRIVATE SECTOR BANKS":
            current_section = "Foreign"  # Next section is Foreign
            continue
        elif b_upper == "FOREIGN BANKS":
            current_section = "SFB"      # Next section is SFB (or All SCB)
            continue
        elif b_upper in ["SMALL FINANCE BANKS", "ALL SCHEDULED COMMERCIAL BANKS"]:
            continue
            
        def to_float(val):
            if val is None or str(val).strip() in ["-", "..", "", "NA"]:
                return np.nan
            try:
                return float(val)
            except:
                return np.nan

        gnpa = to_float(row[3])
        adv = to_float(row[4])
        
        if adv and not np.isnan(adv) and adv > 0:
            bank_records.append({
                "year": current_year,
                "bank": bank_raw,
                "bank_clean": _clean_bank_name(bank_raw),
                "bank_group": current_section,
                "gross_npa_cr": gnpa,
                "gross_adv_cr": adv,
            })
    wb.close()
    
    df_gnpa = pd.DataFrame(bank_records)
    # Deduplicate in case of duplicate reporting
    df_gnpa = df_gnpa.drop_duplicates(subset=["year", "bank_clean"]).reset_index(drop=True)

    # Step 2: Read F5_T11 ratios
    wb_r = openpyxl.load_workbook(ratios_file, read_only=True, data_only=True)
    ws_r = wb_r["Report 1"]
    ratios = []
    curr_yr = None
    for row in ws_r.iter_rows(values_only=True):
        if row[1] and str(row[1]).strip().isdigit():
            curr_yr = int(str(row[1]).strip())
        b_raw = str(row[2]).strip() if len(row) > 2 and row[2] else ""
        if not curr_yr or not b_raw:
            continue
        def pf(v):
            if v is None or str(v).strip() in ["-", "..", "", "NA", " "]:
                return np.nan
            try:
                return float(v)
            except:
                return np.nan
        ratios.append({
            "year": curr_yr,
            "bank_clean": _clean_bank_name(b_raw),
            "cd_ratio": pf(row[4]),       # Credit-Deposit
            "nim": pf(row[14]),           # Net Interest Margin
            "operating_profit_ratio": pf(row[22]),
            "roa": pf(row[23]),           # Return on Assets
            "roe": pf(row[24]),           # Return on Equity
            "cost_of_funds": pf(row[27]), # Cost of Funds
            "crar": pf(row[34]),          # Capital Adequacy Ratio
            "tier1_ratio": pf(row[35]),   # Tier 1 Capital
        })
    wb_r.close()
    df_ratios = pd.DataFrame(ratios).drop_duplicates(subset=["year", "bank_clean"]).reset_index(drop=True)

    # Step 3: Read F7_NPA_MOVEMENT (PCR, Additions, Write-offs)
    wb_m = openpyxl.load_workbook(movement_file, read_only=True, data_only=True)
    ws_m = wb_m["Report 1"]
    movements = []
    curr_yr = None
    for row in ws_m.iter_rows(values_only=True):
        if row[1] and str(row[1]).strip().isdigit():
            curr_yr = int(str(row[1]).strip())
        b_raw = str(row[2]).strip() if len(row) > 2 and row[2] else ""
        if not curr_yr or not b_raw:
            continue
        def pf(v):
            if v is None or str(v).strip() in ["-", "..", "", "NA", " "]:
                return np.nan
            try:
                return float(v)
            except:
                return np.nan
        gnpa_c = pf(row[7])
        nnpa_c = pf(row[9])
        pcr = ((1.0 - (nnpa_c / gnpa_c)) * 100.0) if (gnpa_c and nnpa_c and gnpa_c > 0) else np.nan
        movements.append({
            "year": curr_yr,
            "bank_clean": _clean_bank_name(b_raw),
            "slippages_cr": pf(row[4]),
            "writeoffs_cr": pf(row[6]),
            "net_npa_cr": nnpa_c,
            "pcr": pcr
        })
    wb_m.close()
    df_movements = pd.DataFrame(movements).drop_duplicates(subset=["year", "bank_clean"]).reset_index(drop=True)

    # Merge Micro
    merged = pd.merge(df_gnpa, df_ratios, on=["year", "bank_clean"], how="left")
    merged = pd.merge(merged, df_movements, on=["year", "bank_clean"], how="left")
    
    # Merge Macro
    macro_df = pd.read_csv(macro_file)
    panel = pd.merge(merged, macro_df, on="year", how="left")

    # Compute derived variables
    panel = panel.sort_values(["bank_clean", "year"]).reset_index(drop=True)
    panel["gnpa_ratio"] = (panel["gross_npa_cr"] / panel["gross_adv_cr"]) * 100
    panel["credit_growth"] = panel.groupby("bank_clean")["gross_adv_cr"].pct_change() * 100
    panel["credit_growth_lag1"] = panel.groupby("bank_clean")["credit_growth"].shift(1)
    panel["credit_growth_lag2"] = panel.groupby("bank_clean")["credit_growth"].shift(2)
    panel["log_advances"] = np.log(panel["gross_adv_cr"].clip(lower=1.0))

    # Lead Targets
    panel["gnpa_next1yr"] = panel.groupby("bank_clean")["gnpa_ratio"].shift(-1)
    panel["gnpa_next2yr"] = panel.groupby("bank_clean")["gnpa_ratio"].shift(-2)
    
    # PCA Threshold Breaches
    panel["pca_breach_threshold1"] = (panel["gnpa_ratio"] >= 6.0).astype(int)
    panel["pca_breach_threshold2"] = (panel["gnpa_ratio"] >= 9.0).astype(int)
    panel["pca_breach_threshold3"] = (panel["gnpa_ratio"] >= 12.0).astype(int)
    panel["pca_breach_next1yr"] = panel.groupby("bank_clean")["pca_breach_threshold1"].shift(-1)

    # Clean extreme percentage growth artifacts
    panel.loc[panel["credit_growth"] > 200, "credit_growth"] = np.nan
    panel.loc[panel["credit_growth"] < -80, "credit_growth"] = np.nan
    panel.loc[panel["credit_growth_lag2"] > 200, "credit_growth_lag2"] = np.nan
    panel.loc[panel["credit_growth_lag2"] < -80, "credit_growth_lag2"] = np.nan
    panel.loc[panel["pcr"] > 100, "pcr"] = 100.0
    panel.loc[panel["pcr"] < 0, "pcr"] = 0.0

    if save:
        out_csv = data_dir / "bank_level_panel.csv"
        panel.to_csv(out_csv, index=False)
        logger.info("Saved bank-level panel to %s (%d rows, %d banks)", out_csv, len(panel), panel["bank"].nunique())

    return panel
