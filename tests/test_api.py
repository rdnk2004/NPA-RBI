"""
Tests for the FastAPI serving layer.

Uses TestClient with the `with` context manager so the lifespan
handler actually runs (fits the models) before each test module's
tests execute -- omitting `with` would leave app.state unset and every
route would 503.
"""
import pytest
from fastapi.testclient import TestClient

from npa_ews.api import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_root(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "/docs" in r.json()["docs"]


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_drivers_returns_all_features(client):
    from npa_ews import config

    r = client.get("/drivers")
    assert r.status_code == 200
    body = r.json()
    assert {d["feature"] for d in body["drivers"]} == set(config.FEATURES)
    assert body["fe_n_obs"] == 32


def test_validation_includes_all_baseline_models(client):
    r = client.get("/validation")
    assert r.status_code == 200
    models = {row["model"] for row in r.json()["baseline_comparison"]}
    assert "Naive (persistence)" in models
    assert "XGBoost" in models
    assert "Fixed Effects" in models


def test_reliability_flags_psb_and_sfb_low(client):
    r = client.get("/reliability")
    assert r.status_code == 200
    rows = {row["bank_group"]: row for row in r.json()}
    assert rows["PSB"]["reliable"] is False
    assert rows["Foreign"]["reliable"] is True


def test_scenarios_returns_configured_scenarios(client):
    from npa_ews import config

    r = client.get("/scenarios")
    assert r.status_code == 200
    assert len(r.json()) == len(config.STRESS_SCENARIOS)


def test_stress_default(client):
    r = client.get("/stress?n_boot=50")
    assert r.status_code == 200
    body = r.json()
    assert body["threshold"] == 6.0
    assert len(body["results"]) > 0
    # every row must carry a data_confidence caveat
    assert all(row["data_confidence"] for row in body["results"])


def test_stress_rejects_out_of_range_n_boot(client):
    r = client.get("/stress?n_boot=1")
    assert r.status_code == 400

    r = client.get("/stress?n_boot=100000")
    assert r.status_code == 400


def test_stress_psb_tail_risk_is_low_confidence(client):
    r = client.get("/stress?n_boot=100")
    rows = r.json()["results"]
    psb_tail = next(
        row for row in rows
        if row["bank_group"] == "PSB" and "Tail Risk" in row["scenario"]
    )
    assert "LOW CONFIDENCE" in psb_tail["data_confidence"]


def test_custom_stress_baseline_shocks_match_baseline_gnpa(client):
    """Posting all-zero shocks should reproduce each bank_group's 2024
    baseline GNPA almost exactly, with ~zero bootstrap spread -- same
    invariant as run_stress_test's own baseline scenario."""
    r = client.post(
        "/stress/custom",
        json={"gdp_shock": 0, "repo_shock": 0, "credit_shock": 0, "roa_shock": 0, "n_boot": 50},
    )
    assert r.status_code == 200
    for row in r.json()["results"]:
        assert row["std"] < 1e-6


def test_custom_stress_rejects_invalid_n_boot(client):
    r = client.post(
        "/stress/custom",
        json={"gdp_shock": 0, "repo_shock": 0, "credit_shock": 0, "roa_shock": 0, "n_boot": 1},
    )
    assert r.status_code == 422  # pydantic validation error


def test_custom_stress_never_negative(client):
    """A large enough favorable GDP shock (negative coefficient means
    higher GDP growth reduces GNPA) should be floored at 0, never go
    negative, even for a shock large enough to push the raw linear
    projection below zero."""
    r = client.post(
        "/stress/custom",
        json={"gdp_shock": 100, "repo_shock": 0, "credit_shock": 0, "roa_shock": 0, "n_boot": 50},
    )
    assert r.status_code == 200
    for row in r.json()["results"]:
        assert row["point"] >= 0
        assert row["lower"] >= 0
