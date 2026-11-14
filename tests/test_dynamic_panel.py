"""
Tests for Dynamic Panel Econometric Estimation.
Verifies estimation on the longitudinal bank-level panel.
"""
import pytest
import pandas as pd
import numpy as np

from npa_ews.data import load_bank_level_panel, get_bank_level_model_ready

def test_dynamic_panel_estimation():
    from npa_ews.models.dynamic_panel import DynamicPanelEstimator

    df = load_bank_level_panel()
    clean = get_bank_level_model_ready(df)
    
    estimator = DynamicPanelEstimator()
    res = estimator.fit(clean)
    
    assert res is not None
    assert "roa" in res.params
    assert "credit_growth_lag2" in res.params
    # Lagged GNPA persistence parameter alpha must be positive and substantial (typically 0.4 to 0.8)
    assert res.lag_persistence > 0.2
    assert res.n_obs >= 300
    assert res.n_entities >= 30

def test_dynamic_vs_static_comparison():
    from npa_ews.models.dynamic_panel import DynamicPanelEstimator

    df = load_bank_level_panel()
    clean = get_bank_level_model_ready(df)
    
    estimator = DynamicPanelEstimator()
    comparison_table = estimator.compare_static_vs_dynamic(clean)
    
    assert isinstance(comparison_table, pd.DataFrame)
    assert "Static Fixed Effects" in comparison_table.columns
    assert "Dynamic Panel (IV/FD)" in comparison_table.columns
