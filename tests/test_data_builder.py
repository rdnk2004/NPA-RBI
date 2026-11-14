"""
Tests for data_builder: verifying that both the restored macro bank-group panel
and the granular bank-level panel are correctly extracted from raw RBI files.
"""
from pathlib import Path
import pandas as pd
import pytest

from npa_ews import config

def test_restored_banking_panel_has_full_psb_history():
    """PSB must have observations extending back to 2005, not just 2018."""
    from npa_ews.data_builder import build_macro_banking_panel
    df = build_macro_banking_panel(save=False)
    psb_df = df[df["bank_group"] == "PSB"]
    assert len(psb_df) >= 18, f"Expected >= 18 PSB years, got {len(psb_df)}"
    assert psb_df["year"].min() <= 2005, f"Expected min year <= 2005, got {psb_df['year'].min()}"
    assert psb_df["year"].max() >= 2024
    # The AQR peak in 2017-2018 must be visible in PSB GNPA
    peak_gnpa = psb_df[psb_df["year"].isin([2016, 2017, 2018])]["gnpa_ratio"].max()
    assert peak_gnpa > 10.0, f"Expected AQR peak GNPA > 10%, got {peak_gnpa}"

def test_bank_level_panel_extraction():
    """Bank-level panel must contain individual scheduled commercial banks."""
    from npa_ews.data_builder import build_bank_level_panel
    df = build_bank_level_panel(save=False)
    assert len(df) >= 400, f"Expected >= 400 bank-year observations, got {len(df)}"
    assert df["bank"].nunique() >= 30, f"Expected >= 30 banks, got {df['bank'].nunique()}"
    
    # Must include major anchor banks across groups
    known_banks = {"STATE BANK OF INDIA", "BANK OF BARODA", "PUNJAB NATIONAL BANK", "HDFC BANK LTD.", "ICICI BANK LIMITED", "AXIS BANK LIMITED"}
    present_banks = set(df["bank"].str.upper().unique())
    for kb in known_banks:
        assert any(kb in b for b in present_banks), f"Missing anchor bank {kb}"

    # Must contain critical micro-prudential features
    expected_cols = [
        "year", "bank", "bank_group", "gnpa_ratio", "gross_adv_cr",
        "credit_growth", "roa", "cd_ratio", "crar", "pcr",
        "gnpa_next1yr", "pca_breach_next1yr"
    ]
    for col in expected_cols:
        assert col in df.columns, f"Missing expected column: {col}"
