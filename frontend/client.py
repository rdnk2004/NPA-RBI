"""
Thin HTTP client for the NPA EWS FastAPI backend.

Deliberately separate from app.py: the frontend is a real client of
the API over HTTP (not an import of npa_ews internals), and keeping
the HTTP calls in their own module means they can be unit tested with
a mocked `requests` module, independent of Streamlit's own runtime.
"""
from __future__ import annotations

import requests

DEFAULT_TIMEOUT = 60


class ApiError(RuntimeError):
    """Raised when the backend returns a non-2xx response or is unreachable."""


def _get(base_url: str, path: str, params: dict | None = None) -> dict | list:
    try:
        resp = requests.get(f"{base_url}{path}", params=params, timeout=DEFAULT_TIMEOUT)
    except requests.exceptions.RequestException as exc:
        raise ApiError(f"Could not reach API at {base_url}{path}: {exc}") from exc
    if resp.status_code >= 400:
        raise ApiError(f"{path} returned {resp.status_code}: {resp.text}")
    return resp.json()


def _post(base_url: str, path: str, json_body: dict) -> dict | list:
    try:
        resp = requests.post(f"{base_url}{path}", json=json_body, timeout=DEFAULT_TIMEOUT)
    except requests.exceptions.RequestException as exc:
        raise ApiError(f"Could not reach API at {base_url}{path}: {exc}") from exc
    if resp.status_code >= 400:
        raise ApiError(f"{path} returned {resp.status_code}: {resp.text}")
    return resp.json()


def health(base_url: str) -> dict:
    return _get(base_url, "/health")


def get_drivers(base_url: str) -> dict:
    return _get(base_url, "/drivers")


def get_validation(base_url: str) -> dict:
    return _get(base_url, "/validation")


def get_reliability(base_url: str) -> list:
    return _get(base_url, "/reliability")


def get_scenarios(base_url: str) -> list:
    return _get(base_url, "/scenarios")


def get_stress(base_url: str, n_boot: int = 300) -> dict:
    return _get(base_url, "/stress", params={"n_boot": n_boot})


def post_custom_stress(
    base_url: str, gdp_shock: float, repo_shock: float, credit_shock: float, roa_shock: float, n_boot: int = 300
) -> dict:
    return _post(
        base_url,
        "/stress/custom",
        {
            "gdp_shock": gdp_shock,
            "repo_shock": repo_shock,
            "credit_shock": credit_shock,
            "roa_shock": roa_shock,
            "n_boot": n_boot,
        },
    )


def post_narrative(
    base_url: str,
    bank_group: str,
    *,
    scenario_name: str | None = None,
    gdp_shock: float = 0.0,
    repo_shock: float = 0.0,
    credit_shock: float = 0.0,
    roa_shock: float = 0.0,
    n_boot: int = 200,
) -> dict:
    return _post(
        base_url,
        "/narrative",
        {
            "bank_group": bank_group,
            "scenario_name": scenario_name,
            "gdp_shock": gdp_shock,
            "repo_shock": repo_shock,
            "credit_shock": credit_shock,
            "roa_shock": roa_shock,
            "n_boot": n_boot,
        },
    )
