import numpy as np

from npa_ews import validation


def test_compare_baselines_includes_all_models(model_ready_panel):
    result = validation.compare_baselines(model_ready_panel)
    expected_models = {
        "Naive (persistence)",
        "Historical mean",
        "Pooled OLS (no fixed effects)",
        "Fixed Effects",
        "XGBoost",
    }
    assert set(result.index) == expected_models


def test_compare_baselines_metrics_are_finite(model_ready_panel):
    result = validation.compare_baselines(model_ready_panel)
    assert np.isfinite(result.to_numpy()).all()
    assert (result.to_numpy() >= 0).all()


def test_naive_baseline_uses_current_year_value(model_ready_panel):
    """The naive predictor must literally be this year's gnpa_ratio --
    if it silently used something else (e.g. the target itself), the
    baseline comparison would be meaningless."""
    from npa_ews import config
    from npa_ews.validation import _naive_predict

    test_slice = model_ready_panel.iloc[:3]
    preds = _naive_predict(model_ready_panel, test_slice, config.TARGET)
    np.testing.assert_array_equal(preds, test_slice["gnpa_ratio"].to_numpy())


def test_mean_baseline_uses_training_group_means_only(model_ready_panel):
    """The historical-mean predictor must be computed from TRAIN data
    only -- using test-period means would leak future information."""
    from npa_ews import config
    from npa_ews.validation import _mean_predict

    cutoff = sorted(model_ready_panel["year"].unique())[5]
    train = model_ready_panel[model_ready_panel["year"] <= cutoff]
    test = model_ready_panel[model_ready_panel["year"] == cutoff + 1]

    preds = _mean_predict(train, test, config.TARGET)
    expected = test["bank_group"].map(train.groupby("bank_group")[config.TARGET].mean())
    np.testing.assert_array_almost_equal(preds, expected.to_numpy())
