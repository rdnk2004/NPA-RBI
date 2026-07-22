"""
LLM narrative explainer: turns structured stress-test output + SHAP
drivers into a short, plain-English supervisory risk narrative.

This is the one LLM integration in this project, placed here
deliberately rather than bolted on elsewhere: the policy note already
does this translation by hand ("declining profitability is the
earliest internal supervisory warning signal..."). This module
automates exactly that step, using the same numbers the rest of the
system computes and tests. It narrates existing, validated output --
it does not invent new analysis, and the prompt explicitly forbids
the model from adding numbers beyond what it's given.

Requires ANTHROPIC_API_KEY in the environment. Fails gracefully (a
clear "not configured" result, not an exception) if it isn't set --
every other endpoint in this API must keep working even if this one
can't reach an LLM.
"""
from __future__ import annotations

import os
from dataclasses import dataclass

import requests

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
DEFAULT_MODEL = "claude-sonnet-4-6"
NOT_CONFIGURED_MESSAGE = (
    "LLM narrative generation is not configured (ANTHROPIC_API_KEY is not set in "
    "the environment). Set that environment variable and restart the API to enable "
    "this feature; every other endpoint works without it."
)


@dataclass
class NarrativeResult:
    narrative: str
    generated: bool
    model: str | None = None


def is_configured() -> bool:
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def build_prompt(
    bank_group: str,
    scenario_name: str,
    point: float,
    lower: float,
    upper: float,
    breach_probability: float,
    threshold: float,
    data_confidence: str,
    drivers: list[dict],
) -> str:
    driver_lines = "\n".join(
        f"- {d['label']}: FE coefficient {d['fe_coefficient']}, SHAP importance {d['shap_importance']}"
        for d in drivers
    )
    return f"""You are drafting a short risk narrative for an RBI bank supervision offsite surveillance note.

Bank group: {bank_group}
Scenario: {scenario_name}
Projected GNPA: {point:.2f}% (90% CI: [{lower:.2f}%, {upper:.2f}%])
Probability of breaching PCA Threshold 1 ({threshold:.1f}%): {breach_probability:.1%}
Data confidence: {data_confidence}

Key drivers identified by the underlying models (Fixed Effects regression coefficient and XGBoost SHAP importance):
{driver_lines}

Write a 3-4 sentence supervisory risk narrative for this bank group and scenario. State the breach probability explicitly rather than treating this as a precise point forecast. Reference at most one driver by name. If data confidence is LOW CONFIDENCE, say so explicitly and note the figure should not be read as more precise than that caveat allows. Do not invent numbers beyond what is given here. Do not add policy recommendations -- describe the risk only."""


def generate_narrative(
    *,
    bank_group: str,
    scenario_name: str,
    point: float,
    lower: float,
    upper: float,
    breach_probability: float,
    threshold: float,
    data_confidence: str,
    drivers: list[dict],
    model: str = DEFAULT_MODEL,
    timeout: float = 30.0,
) -> NarrativeResult:
    if not is_configured():
        return NarrativeResult(narrative=NOT_CONFIGURED_MESSAGE, generated=False)

    prompt = build_prompt(
        bank_group, scenario_name, point, lower, upper,
        breach_probability, threshold, data_confidence, drivers,
    )
    response = requests.post(
        ANTHROPIC_API_URL,
        headers={
            "x-api-key": os.environ["ANTHROPIC_API_KEY"],
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": model,
            "max_tokens": 300,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=timeout,
    )
    response.raise_for_status()
    payload = response.json()
    text = "".join(
        block["text"] for block in payload.get("content", []) if block.get("type") == "text"
    )
    return NarrativeResult(narrative=text.strip(), generated=True, model=model)
