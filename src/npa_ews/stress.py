"""
Macro stress testing: translate scenario shocks into projected GNPA
via fixed-effects regression coefficients.

Extracted from 05_stress_test.py. Takes a fitted FixedEffectsRegressor
so the stress test always uses coefficients from a single, testable
source rather than re-fitting its own copy.
"""
from __future__ import annotations

import pandas as pd

from npa_ews import config
from npa_ews.models.panel_fe import FEResult

# PCA (Prompt Corrective Action) Risk Threshold 1, per RBI framework.
PCA_THRESHOLD_1 = 6.0


def run_stress_test(
    fe_result: FEResult,
    baseline: pd.DataFrame,
    scenarios: list[config.StressScenario] | None = None,
) -> pd.DataFrame:
    """Apply each stress scenario's shocks to the baseline GNPA ratio.

    Parameters
    ----------
    fe_result:
        Output of FixedEffectsRegressor.fit(...) -- supplies the
        coefficients used to translate macro shocks into GNPA impact.
    baseline:
        DataFrame indexed by bank_group with a 'gnpa_ratio' column
        (typically the most recent actual year).
    scenarios:
        List of StressScenario; defaults to config.STRESS_SCENARIOS.

    Returns
    -------
    DataFrame indexed by bank_group, one column per scenario, values
    are projected GNPA ratio (%), floored at 0.
    """
    scenarios = scenarios or config.STRESS_SCENARIOS
    coefs = fe_result.coefficients

    results: dict[str, dict[str, float]] = {}
    for scenario in scenarios:
        gnpa_impact = (
            coefs["gdp_growth"] * scenario.gdp_shock
            + coefs["repo_rate"] * scenario.repo_shock
            + coefs["credit_growth_lag2"] * scenario.credit_shock
            + coefs["roa"] * scenario.roa_shock
        )
        stressed = {
            bg: round(max(0.0, baseline.loc[bg, "gnpa_ratio"] + gnpa_impact), 3)
            for bg in baseline.index
        }
        results[scenario.name] = stressed

    return pd.DataFrame(results)


def find_pca_breaches(
    stress_df: pd.DataFrame, threshold: float = PCA_THRESHOLD_1
) -> dict[str, dict[str, float]]:
    """For each scenario column, return {bank_group: gnpa} for groups
    that breach the PCA threshold."""
    breaches: dict[str, dict[str, float]] = {}
    for col in stress_df.columns:
        col_breaches = stress_df[stress_df[col] > threshold][col]
        if len(col_breaches):
            breaches[col] = col_breaches.round(2).to_dict()
    return breaches
