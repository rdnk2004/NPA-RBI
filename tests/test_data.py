import pandas as pd
import pytest

from npa_ews.data import SchemaError, _validate_schema, get_model_ready_frame


def test_valid_panel_passes(synthetic_panel, tmp_path):
    path = tmp_path / "panel.csv"
    _validate_schema(synthetic_panel, path)  # should not raise


def test_missing_column_raises(synthetic_panel, tmp_path):
    broken = synthetic_panel.drop(columns=["roa"])
    with pytest.raises(SchemaError, match="missing required columns"):
        _validate_schema(broken, tmp_path / "panel.csv")


def test_unexpected_bank_group_raises(synthetic_panel, tmp_path):
    broken = synthetic_panel.copy()
    broken.loc[0, "bank_group"] = "Cooperative"  # not in config.BANK_GROUPS
    with pytest.raises(SchemaError, match="unexpected bank_group"):
        _validate_schema(broken, tmp_path / "panel.csv")


def test_negative_gnpa_raises(synthetic_panel, tmp_path):
    broken = synthetic_panel.copy()
    broken.loc[0, "gnpa_ratio"] = -1.0
    with pytest.raises(SchemaError, match="negative gnpa_ratio"):
        _validate_schema(broken, tmp_path / "panel.csv")


def test_implausible_gnpa_raises(synthetic_panel, tmp_path):
    broken = synthetic_panel.copy()
    broken.loc[0, "gnpa_ratio"] = 99.0
    with pytest.raises(SchemaError, match="implausible"):
        _validate_schema(broken, tmp_path / "panel.csv")


def test_duplicate_year_bank_group_raises(synthetic_panel, tmp_path):
    broken = pd.concat([synthetic_panel, synthetic_panel.iloc[[0]]], ignore_index=True)
    with pytest.raises(SchemaError, match="duplicate"):
        _validate_schema(broken, tmp_path / "panel.csv")


def test_get_model_ready_frame_drops_nulls(synthetic_panel):
    ml_df = get_model_ready_frame(synthetic_panel)
    # last year per bank_group has no gnpa_next1yr -> must be dropped
    assert ml_df["gnpa_next1yr"].isna().sum() == 0
    assert len(ml_df) < len(synthetic_panel)
