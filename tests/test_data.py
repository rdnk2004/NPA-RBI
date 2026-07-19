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


def test_group_reliability_flags_low_obs_groups(model_ready_panel):
    from npa_ews import config
    from npa_ews.data import group_reliability

    reliability = group_reliability(model_ready_panel)
    assert set(reliability.index) == set(config.BANK_GROUPS)
    for bg in config.BANK_GROUPS:
        expected = reliability.loc[bg, "n_obs"] >= config.MIN_RELIABLE_OBS
        assert reliability.loc[bg, "reliable"] == expected


def test_group_reliability_with_synthetic_data_all_reliable(model_ready_panel):
    """The synthetic fixture gives every group ~9 years -- comfortably
    above MIN_RELIABLE_OBS -- so nothing should be flagged low-confidence
    here. (The real dataset's PSB/SFB scarcity is a property of the
    real data, not something this function should invent.)"""
    from npa_ews.data import group_reliability

    reliability = group_reliability(model_ready_panel)
    assert reliability["reliable"].all()


def test_annotate_reliability_flags_low_confidence_groups():
    import pandas as pd

    from npa_ews.data import annotate_reliability, group_reliability

    ml_df = pd.DataFrame(
        {
            "bank_group": ["PSB"] * 4 + ["Private"] * 12,
            "year": list(range(2021, 2025)) + list(range(2013, 2025)),
        }
    )
    reliability = group_reliability(ml_df)

    sample = pd.DataFrame({"gnpa": [6.1, 2.0]}, index=["PSB", "Private"])
    sample.index.name = "bank_group"

    annotated = annotate_reliability(sample, reliability)
    assert "LOW CONFIDENCE" in annotated.loc["PSB", "data_confidence"]
    assert "reliable" in annotated.loc["Private", "data_confidence"]


def test_annotate_reliability_handles_group_with_no_data():
    import pandas as pd

    from npa_ews.data import annotate_reliability, group_reliability

    ml_df = pd.DataFrame({"bank_group": ["Private"] * 12, "year": range(2013, 2025)})
    reliability = group_reliability(ml_df)  # PSB/Foreign/SFB will be all-NaN rows

    sample = pd.DataFrame({"gnpa": [5.0]}, index=["SFB"])
    sample.index.name = "bank_group"

    annotated = annotate_reliability(sample, reliability)
    assert annotated.loc["SFB", "data_confidence"] == "no data"
