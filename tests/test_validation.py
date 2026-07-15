import numpy as np
import pytest

from npa_ews import validation


def test_walk_forward_cv_produces_folds(model_ready_panel):
    result = validation.walk_forward_cv(model_ready_panel, min_train_years=5)
    assert len(result.folds) > 0


def test_folds_never_train_on_future(model_ready_panel):
    """Each fold's train_year_range max must be strictly before its
    test_year -- the core temporal-integrity guarantee of walk-forward
    CV. If this ever fails, the CV has silently become leaky."""
    result = validation.walk_forward_cv(model_ready_panel, min_train_years=5)
    for fold in result.folds:
        assert fold.train_year_range[1] < fold.test_year


def test_folds_are_expanding_not_shrinking(model_ready_panel):
    result = validation.walk_forward_cv(model_ready_panel, min_train_years=5)
    train_sizes = [f.n_train for f in result.folds]
    assert train_sizes == sorted(train_sizes)


def test_summary_metrics_are_finite_and_nonnegative(model_ready_panel):
    result = validation.walk_forward_cv(model_ready_panel, min_train_years=5)
    for metric in (result.mean_mae, result.std_mae, result.mean_rmse, result.std_rmse):
        assert np.isfinite(metric)
        assert metric >= 0


def test_too_few_years_raises(model_ready_panel):
    with pytest.raises(ValueError, match="distinct years"):
        validation.walk_forward_cv(model_ready_panel, min_train_years=100)


def test_summary_table_has_one_row_per_fold(model_ready_panel):
    result = validation.walk_forward_cv(model_ready_panel, min_train_years=5)
    table = result.summary_table()
    assert len(table) == len(result.folds)
    assert set(table.columns) == {
        "train_years", "test_year", "n_train", "n_test", "mae", "rmse"
    }
