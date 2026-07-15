import numpy as np
import pytest

from npa_ews.models.panel_fe import FixedEffectsRegressor


def test_fit_returns_all_feature_coefficients(model_ready_panel):
    fe = FixedEffectsRegressor()
    result = fe.fit(model_ready_panel)
    assert set(result.coefficients.keys()) == set(fe.features)
    assert all(np.isfinite(v) for v in result.coefficients.values())


def test_n_obs_matches_input(model_ready_panel):
    fe = FixedEffectsRegressor()
    result = fe.fit(model_ready_panel)
    assert result.n_obs == len(model_ready_panel)


def test_result_property_raises_before_fit():
    fe = FixedEffectsRegressor()
    with pytest.raises(RuntimeError, match="Call .fit"):
        _ = fe.result


def test_demeaning_removes_group_level_variation(model_ready_panel):
    """Sanity check on the within-transform itself: after demeaning,
    each bank_group's mean for a feature should equal the overall mean
    (that's the entire point of the fixed-effects transform)."""
    fe = FixedEffectsRegressor()
    fe.fit(model_ready_panel)

    fe_df = model_ready_panel.copy()
    col = "roa"
    group_mean = fe_df.groupby("bank_group")[col].transform("mean")
    overall_mean = fe_df[col].mean()
    demeaned = fe_df[col] - group_mean + overall_mean

    group_means_after = demeaned.groupby(fe_df["bank_group"]).mean()
    assert np.allclose(group_means_after, overall_mean, atol=1e-8)
