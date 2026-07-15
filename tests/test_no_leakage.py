"""
Leakage tests.

For any model whose whole premise is "predict next year from this
year's data", the single most damaging bug is silent leakage: test
rows that share information with train rows, or a target that's
trivially reconstructable from a feature. These tests exist to catch
that class of bug before it inflates a reported R^2.
"""
import numpy as np
import pandas as pd

from npa_ews import config
from npa_ews.models.xgb_model import GnpaXGBModel


def _temporal_split(ml_df: pd.DataFrame):
    train = ml_df[ml_df["year"] <= config.TRAIN_YEAR_MAX]
    test = ml_df[ml_df["year"] >= config.TEST_YEAR_MIN]
    return train, test


def test_train_test_years_do_not_overlap(model_ready_panel):
    train, test = _temporal_split(model_ready_panel)
    assert train["year"].max() < test["year"].min()


def test_train_and_test_are_nonempty(model_ready_panel):
    train, test = _temporal_split(model_ready_panel)
    assert len(train) > 0
    assert len(test) > 0


def test_target_is_not_a_feature(model_ready_panel):
    """The target column must never appear in the feature list --
    trivial, but this exact bug (accidentally including a
    contemporaneous or future column) is the most common source of
    a suspiciously perfect model."""
    assert config.TARGET not in config.FEATURES


def test_target_is_actually_shifted_forward(synthetic_panel):
    """gnpa_next1yr for year Y, bank_group G must equal gnpa_ratio for
    year Y+1, same bank_group -- i.e. it really is a forward-looking
    target, not an accidental same-year copy of the ratio itself."""
    df = synthetic_panel.sort_values(["bank_group", "year"])
    for bg, grp in df.groupby("bank_group"):
        grp = grp.sort_values("year").reset_index(drop=True)
        for i in range(len(grp) - 1):
            if pd.notna(grp.loc[i, "gnpa_next1yr"]):
                assert np.isclose(
                    grp.loc[i, "gnpa_next1yr"], grp.loc[i + 1, "gnpa_ratio"]
                )


def test_model_does_not_memorize_train_perfectly(model_ready_panel):
    """With max_depth=2 and regularization, train R^2 should be well
    below 1.0. A train R^2 near 1.0 would indicate the regularization
    isn't actually constraining the model -- a regression bug, since
    the whole point of the shallow-tree design is to avoid this on
    n~32."""
    train, test = _temporal_split(model_ready_panel)
    model = GnpaXGBModel().fit(train, test)
    metrics = model.evaluate(train, test)
    assert metrics.train_r2 < 0.999
