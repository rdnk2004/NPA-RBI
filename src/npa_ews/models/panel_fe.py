"""
Fixed-effects panel regression via the within (demeaning) transform.

Extracted from the original 03_panel_regression.py / 05_stress_test.py,
which each re-implemented the same demeaning logic inline. Having it
once, as a class with a documented fit/coefficient interface, is what
lets 05's stress test and any future scenario tool *reuse* a fitted
model instead of recomputing it from a copy-pasted block.
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import statsmodels.api as sm

from npa_ews import config


@dataclass
class FEResult:
    model: sm.regression.linear_model.RegressionResultsWrapper
    coefficients: dict[str, float]
    r_squared: float
    n_obs: int


class FixedEffectsRegressor:
    """Bank-group fixed-effects regression of TARGET on FEATURES.

    Uses the within transform: demean each feature and the target by
    bank_group, then run pooled OLS with robust (HC3) standard errors.
    Mathematically equivalent to including bank_group dummies, without
    burning degrees of freedom on the intercepts -- important with
    only ~32 usable observations.
    """

    def __init__(self, features: list[str] | None = None, target: str | None = None):
        self.features = features or config.FEATURES
        self.target = target or config.TARGET
        self._result: FEResult | None = None

    def fit(self, df: pd.DataFrame) -> FEResult:
        fe_df = df.copy()
        for col in self.features + [self.target]:
            group_mean = fe_df.groupby("bank_group")[col].transform("mean")
            overall_mean = fe_df[col].mean()
            fe_df[f"{col}_dm"] = fe_df[col] - group_mean + overall_mean

        X = sm.add_constant(fe_df[[f"{f}_dm" for f in self.features]])
        y = fe_df[f"{self.target}_dm"]
        model = sm.OLS(y, X).fit(cov_type="HC3")

        coefficients = {f: model.params[f"{f}_dm"] for f in self.features}

        self._result = FEResult(
            model=model,
            coefficients=coefficients,
            r_squared=model.rsquared,
            n_obs=int(model.nobs),
        )
        return self._result

    @property
    def result(self) -> FEResult:
        if self._result is None:
            raise RuntimeError("Call .fit(df) before accessing results.")
        return self._result

    def summary(self) -> str:
        return str(self.result.model.summary())
