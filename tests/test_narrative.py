import pytest

from npa_ews import narrative


@pytest.fixture
def sample_drivers():
    return [
        {"label": "Return on Assets", "fe_coefficient": -2.3327, "shap_importance": 0.5868},
        {"label": "Provision Coverage Ratio", "fe_coefficient": -0.0488, "shap_importance": 0.2097},
    ]


def test_not_configured_when_no_api_key(monkeypatch, sample_drivers):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    result = narrative.generate_narrative(
        bank_group="PSB",
        scenario_name="Tail Risk (COVID FY21)",
        point=6.09, lower=4.40, upper=7.07,
        breach_probability=0.643, threshold=6.0,
        data_confidence="LOW CONFIDENCE (n=4)",
        drivers=sample_drivers,
    )
    assert result.generated is False
    assert "not configured" in result.narrative.lower()


def test_is_configured_reflects_env_var(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    assert narrative.is_configured() is False
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-fake-key-for-testing")
    assert narrative.is_configured() is True


def test_generate_narrative_with_mocked_api_call(monkeypatch, sample_drivers):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-fake-key-for-testing")

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "content": [
                    {"type": "text", "text": "PSB carries a 64% probability of breaching the PCA threshold."}
                ]
            }

    def fake_post(url, headers=None, json=None, timeout=None):
        assert url == narrative.ANTHROPIC_API_URL
        assert headers["x-api-key"] == "sk-fake-key-for-testing"
        assert "PSB" in json["messages"][0]["content"]
        return FakeResponse()

    monkeypatch.setattr(narrative.requests, "post", fake_post)

    result = narrative.generate_narrative(
        bank_group="PSB",
        scenario_name="Tail Risk (COVID FY21)",
        point=6.09, lower=4.40, upper=7.07,
        breach_probability=0.643, threshold=6.0,
        data_confidence="LOW CONFIDENCE (n=4)",
        drivers=sample_drivers,
    )
    assert result.generated is True
    assert "64%" in result.narrative
    assert result.model == narrative.DEFAULT_MODEL


def test_build_prompt_includes_key_figures(sample_drivers):
    prompt = narrative.build_prompt(
        bank_group="PSB",
        scenario_name="Tail Risk (COVID FY21)",
        point=6.09, lower=4.40, upper=7.07,
        breach_probability=0.643, threshold=6.0,
        data_confidence="LOW CONFIDENCE (n=4)",
        drivers=sample_drivers,
    )
    assert "PSB" in prompt
    assert "64.3%" in prompt
    assert "LOW CONFIDENCE" in prompt
    assert "Return on Assets" in prompt


def test_generate_narrative_does_not_call_network_when_unconfigured(monkeypatch, sample_drivers):
    """If the API key is missing, generate_narrative must return early
    -- it must never attempt a network call that would just fail with
    a 401 or hang on a bad connection."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    def fail_if_called(*args, **kwargs):
        raise AssertionError("requests.post should not be called when unconfigured")

    monkeypatch.setattr(narrative.requests, "post", fail_if_called)

    result = narrative.generate_narrative(
        bank_group="Foreign",
        scenario_name="Baseline (2024 actuals)",
        point=1.19, lower=1.19, upper=1.19,
        breach_probability=0.0, threshold=6.0,
        data_confidence="reliable (n=12)",
        drivers=sample_drivers,
    )
    assert result.generated is False
