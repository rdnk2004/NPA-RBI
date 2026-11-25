"""
Tests for Bank-Level Machine Learning & PCA Breach Classification.
"""
import pytest
import pandas as pd
import numpy as np

from npa_ews.data import load_bank_level_panel, get_bank_level_model_ready

def test_bank_level_xgb_regression():
    from npa_ews.models.xgb_model import GnpaXGBModel
    from npa_ews import config

    df = load_bank_level_panel()
    clean = get_bank_level_model_ready(df, features=config.BANK_LEVEL_FEATURES, target="gnpa_next1yr")
    
    train = clean[clean["year"] <= 2021]
    test = clean[clean["year"] >= 2022]
    
    model = GnpaXGBModel(features=config.BANK_LEVEL_FEATURES, target="gnpa_next1yr")
    model.fit(train, test)
    
    preds = model.predict(test)
    assert len(preds) == len(test)
    metrics = model.evaluate(train, test)
    assert metrics.test_mae < 3.5  # reasonable error bound on diverse bank panel
    assert len(model.global_importance(clean)) == len(config.BANK_LEVEL_FEATURES)

def test_pca_breach_classifier():
    from npa_ews.models.xgb_model import PcaBreachClassifier
    from npa_ews import config

    df = load_bank_level_panel()
    clean = get_bank_level_model_ready(df, features=config.BANK_LEVEL_FEATURES, target="pca_breach_next1yr")
    
    train = clean[clean["year"] <= 2021]
    test = clean[clean["year"] >= 2022]
    
    clf = PcaBreachClassifier(features=config.BANK_LEVEL_FEATURES, target="pca_breach_next1yr")
    clf.fit(train)
    
    probs = clf.predict_proba(test)
    assert len(probs) == len(test)
    assert (probs >= 0.0).all() and (probs <= 1.0).all()
    
    eval_res = clf.evaluate(test)
    assert eval_res["roc_auc"] > 0.65  # meaningful predictive discrimination
