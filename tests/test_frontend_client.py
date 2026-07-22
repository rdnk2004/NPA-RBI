import sys
from pathlib import Path

import pytest

# frontend/ is a standalone app, not part of the installed npa_ews
# package, so it isn't on sys.path by default -- add it explicitly.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "frontend"))

import client  # noqa: E402


class FakeResponse:
    def __init__(self, status_code=200, json_data=None, text=""):
        self.status_code = status_code
        self._json_data = json_data or {}
        self.text = text

    def json(self):
        return self._json_data


def test_get_drivers_calls_correct_url(monkeypatch):
    captured = {}

    def fake_get(url, params=None, timeout=None):
        captured["url"] = url
        return FakeResponse(200, {"drivers": []})

    monkeypatch.setattr(client.requests, "get", fake_get)
    result = client.get_drivers("http://localhost:8000")
    assert captured["url"] == "http://localhost:8000/drivers"
    assert result == {"drivers": []}


def test_get_stress_passes_n_boot_param(monkeypatch):
    captured = {}

    def fake_get(url, params=None, timeout=None):
        captured["params"] = params
        return FakeResponse(200, {"results": []})

    monkeypatch.setattr(client.requests, "get", fake_get)
    client.get_stress("http://localhost:8000", n_boot=500)
    assert captured["params"] == {"n_boot": 500}


def test_error_response_raises_api_error(monkeypatch):
    def fake_get(url, params=None, timeout=None):
        return FakeResponse(404, text="not found")

    monkeypatch.setattr(client.requests, "get", fake_get)
    with pytest.raises(client.ApiError, match="404"):
        client.get_drivers("http://localhost:8000")


def test_connection_error_raises_api_error(monkeypatch):
    import requests as real_requests

    def fake_get(url, params=None, timeout=None):
        raise real_requests.exceptions.ConnectionError("refused")

    monkeypatch.setattr(client.requests, "get", fake_get)
    with pytest.raises(client.ApiError, match="Could not reach API"):
        client.health("http://localhost:8000")


def test_post_custom_stress_sends_all_shock_fields(monkeypatch):
    captured = {}

    def fake_post(url, json=None, timeout=None):
        captured["url"] = url
        captured["json"] = json
        return FakeResponse(200, {"results": []})

    monkeypatch.setattr(client.requests, "post", fake_post)
    client.post_custom_stress("http://localhost:8000", gdp_shock=-2.0, repo_shock=0.5, credit_shock=-3.0, roa_shock=-0.1, n_boot=100)
    assert captured["url"] == "http://localhost:8000/stress/custom"
    assert captured["json"] == {
        "gdp_shock": -2.0, "repo_shock": 0.5, "credit_shock": -3.0, "roa_shock": -0.1, "n_boot": 100,
    }


def test_post_narrative_with_scenario_name(monkeypatch):
    captured = {}

    def fake_post(url, json=None, timeout=None):
        captured["json"] = json
        return FakeResponse(200, {"narrative": "test", "generated": False})

    monkeypatch.setattr(client.requests, "post", fake_post)
    client.post_narrative("http://localhost:8000", "PSB", scenario_name="Tail Risk (COVID FY21)")
    assert captured["json"]["bank_group"] == "PSB"
    assert captured["json"]["scenario_name"] == "Tail Risk (COVID FY21)"
