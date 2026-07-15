import pandas as pd

from npa_ews import config
from npa_ews.models.panel_fe import FixedEffectsRegressor
from npa_ews.stress import find_pca_breaches, run_stress_test


def test_baseline_scenario_reproduces_baseline_gnpa(model_ready_panel):
    """The 'Baseline (2024 actuals)' scenario applies zero shocks, so
    its output must exactly equal the input baseline GNPA -- if it
    doesn't, the shock-application arithmetic has a bug."""
    fe_result = FixedEffectsRegressor().fit(model_ready_panel)
    baseline = (
        model_ready_panel[model_ready_panel["year"] == model_ready_panel["year"].max()]
        .set_index("bank_group")
    )
    stress_df = run_stress_test(fe_result, baseline)
    pd.testing.assert_series_equal(
        stress_df["Baseline (2024 actuals)"].sort_index(),
        baseline["gnpa_ratio"].round(3).sort_index(),
        check_names=False,
    )


def test_stressed_gnpa_never_negative(model_ready_panel):
    fe_result = FixedEffectsRegressor().fit(model_ready_panel)
    baseline = (
        model_ready_panel[model_ready_panel["year"] == model_ready_panel["year"].max()]
        .set_index("bank_group")
    )
    stress_df = run_stress_test(fe_result, baseline)
    assert (stress_df >= 0).all().all()


def test_output_has_one_column_per_scenario(model_ready_panel):
    fe_result = FixedEffectsRegressor().fit(model_ready_panel)
    baseline = (
        model_ready_panel[model_ready_panel["year"] == model_ready_panel["year"].max()]
        .set_index("bank_group")
    )
    stress_df = run_stress_test(fe_result, baseline)
    assert len(stress_df.columns) == len(config.STRESS_SCENARIOS)


def test_find_pca_breaches_detects_known_breach():
    stress_df = pd.DataFrame(
        {"Tail Risk": {"PSB": 6.29, "Foreign": 4.01}, "Baseline": {"PSB": 3.47, "Foreign": 1.19}}
    )
    breaches = find_pca_breaches(stress_df, threshold=6.0)
    assert breaches == {"Tail Risk": {"PSB": 6.29}}


def test_find_pca_breaches_empty_when_none_breach():
    stress_df = pd.DataFrame({"Baseline": {"PSB": 3.47, "Foreign": 1.19}})
    assert find_pca_breaches(stress_df, threshold=6.0) == {}


def test_bootstrap_baseline_scenario_has_zero_spread(model_ready_panel):
    """The baseline scenario applies zero shocks, so gnpa_impact = 0
    regardless of which bootstrap coefficients are drawn -- every
    bootstrap draw for baseline must be numerically identical."""
    baseline = (
        model_ready_panel[model_ready_panel["year"] == model_ready_panel["year"].max()]
        .set_index("bank_group")
    )
    from npa_ews.stress import bootstrap_stress_test

    results = bootstrap_stress_test(model_ready_panel, baseline, n_boot=25)
    baseline_result = results["Baseline (2024 actuals)"]
    assert (baseline_result["std"] < 1e-6).all()


def test_bootstrap_intervals_contain_point_estimate(model_ready_panel):
    baseline = (
        model_ready_panel[model_ready_panel["year"] == model_ready_panel["year"].max()]
        .set_index("bank_group")
    )
    from npa_ews.stress import bootstrap_stress_test

    results = bootstrap_stress_test(model_ready_panel, baseline, n_boot=25)
    for scenario_df in results.values():
        assert (scenario_df["lower"] <= scenario_df["point"]).all()
        assert (scenario_df["point"] <= scenario_df["upper"]).all()


def test_bootstrap_breach_prob_between_zero_and_one(model_ready_panel):
    baseline = (
        model_ready_panel[model_ready_panel["year"] == model_ready_panel["year"].max()]
        .set_index("bank_group")
    )
    from npa_ews.stress import bootstrap_stress_test

    results = bootstrap_stress_test(model_ready_panel, baseline, n_boot=25)
    for scenario_df in results.values():
        assert (scenario_df["breach_prob"] >= 0).all()
        assert (scenario_df["breach_prob"] <= 1).all()
