"""
Macro stress testing: translate scenario shocks into projected GNPA
via fixed-effects regression coefficients.

Extracted from 05_stress_test.py. Takes a fitted FixedEffectsRegressor
so the stress test always uses coefficients from a single, testable
source rather than re-fitting its own copy.

v0.3 adds block-bootstrap confidence intervals: the original stress
test reported a single point estimate per scenario (e.g. "PSB -> 6.29%
under Tail Risk"). With n~32, that number carries real sampling
uncertainty the original notebook didn't quantify. bootstrap_stress_test
resamples years *within* each bank_group (preserving panel structure),
refits the FE model hundreds of times, and reports the resulting
percentile interval plus the probability of breaching the PCA
threshold -- turning "marginally breaches 6.0%" into something like
"38% probability of breach", which is what a supervisor actually needs.
"""
from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from npa_ews import config
from npa_ews.models.panel_fe import FEResult, FixedEffectsRegressor

logger = logging.getLogger(__name__)

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


def bootstrap_stress_test(
    ml_df: pd.DataFrame,
    baseline: pd.DataFrame,
    scenarios: list[config.StressScenario] | None = None,
    n_boot: int = 1000,
    ci: float = 0.90,
    threshold: float = PCA_THRESHOLD_1,
    seed: int = config.RANDOM_SEED,
) -> dict[str, pd.DataFrame]:
    """Block-bootstrap uncertainty bands for the stress test.

    Resamples each bank_group's own years with replacement (a block
    bootstrap -- preserves the panel's group structure rather than
    pooling all rows, which would let a resample mix years across
    unrelated bank groups), refits the FE model on each resample, and
    re-runs run_stress_test on every draw. This directly reuses
    run_stress_test rather than reimplementing the shock arithmetic,
    so the bootstrap can't silently drift from the point-estimate
    methodology.

    Parameters
    ----------
    ml_df:
        Model-ready panel used to fit the FE model.
    baseline:
        Same baseline frame passed to run_stress_test (indexed by
        bank_group, has a 'gnpa_ratio' column).
    n_boot:
        Number of bootstrap resamples. 1000 is generous for report
        figures; use a smaller number (e.g. 200) for fast CLI runs.
    ci:
        Confidence level for the percentile interval, e.g. 0.90 for a
        90% interval (5th/95th percentiles).

    Returns
    -------
    dict mapping scenario name -> DataFrame indexed by bank_group with
    columns [point, lower, upper, std, breach_prob]. `breach_prob` is
    the fraction of bootstrap draws exceeding `threshold`.
    """
    scenarios = scenarios or config.STRESS_SCENARIOS
    rng = np.random.default_rng(seed)
    groups = ml_df["bank_group"].unique()

    draws: dict[str, dict[str, list[float]]] = {
        s.name: {bg: [] for bg in baseline.index} for s in scenarios
    }

    n_failed = 0
    for _ in range(n_boot):
        boot_frames = []
        for bg in groups:
            grp = ml_df[ml_df["bank_group"] == bg]
            idx = rng.integers(0, len(grp), size=len(grp))
            boot_frames.append(grp.iloc[idx])
        boot_df = pd.concat(boot_frames, ignore_index=True)

        try:
            fe_result: FEResult = FixedEffectsRegressor().fit(boot_df)
        except Exception:
            # A degenerate resample (e.g. near-zero variance in a
            # feature) can make OLS ill-conditioned. Skip it rather
            # than let one bad draw crash the whole bootstrap.
            n_failed += 1
            continue

        stress_df = run_stress_test(fe_result, baseline, scenarios)
        for s in scenarios:
            for bg in baseline.index:
                draws[s.name][bg].append(stress_df.loc[bg, s.name])

    if n_failed:
        logger.warning("%d/%d bootstrap resamples failed and were skipped.", n_failed, n_boot)

    alpha = (1 - ci) / 2
    results: dict[str, pd.DataFrame] = {}
    for s in scenarios:
        rows = []
        for bg in baseline.index:
            arr = np.array(draws[s.name][bg])
            rows.append(
                {
                    "bank_group": bg,
                    "point": round(float(np.mean(arr)), 3),
                    "lower": round(float(np.percentile(arr, 100 * alpha)), 3),
                    "upper": round(float(np.percentile(arr, 100 * (1 - alpha))), 3),
                    "std": round(float(np.std(arr)), 3),
                    "breach_prob": round(float(np.mean(arr > threshold)), 3),
                }
            )
        results[s.name] = pd.DataFrame(rows).set_index("bank_group")
    return results
