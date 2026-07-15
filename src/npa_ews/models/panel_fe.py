"""
Fixed-effects panel regression via the within (demeaning) transform.

Extracted from the original 03_panel_regression.py / 05_stress_test.py,
which each re-implemented the same demeaning logic inline. Having it
once, as a class with a documented fit/coefficient interface, is what
lets 05's stress test and any future scenario tool *reuse* a fitted
model instead of recomputing it from a copy-pasted block.

v0.3 adds group_intercepts + predict(): the within transform gives you
coefficients but deliberately discards the per-group intercept (that's
the whole point of demeaning). To predict on new rows -- which
walk-forward CV and bootstrapping both need -- you have to recover
that intercept per bank_group:

    alpha_i = mean_i(y) - sum_k( beta_k * mean_i(X_k) )

computed from the *training* data for each group. This is the
standard way to get fitted/predicted values out of a within estimator.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd
import statsmodels.api as sm

from npa_ews import config


@dataclass
class FEResult:
    model: sm.regression.linear_model.RegressionResultsWrapper
    coefficients: dict[str, float]
    r_squared: float
    n_obs: int
    group_intercepts: dict[str, float] = field(default_factory=dict)


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
        group_intercepts = self._recover_group_intercepts(df, coefficients)

        self._result = FEResult(
            model=model,
            coefficients=coefficients,
            r_squared=model.rsquared,
            n_obs=int(model.nobs),
            group_intercepts=group_intercepts,
        )
        return self._result

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        """Out-of-sample prediction using recovered group intercepts.

        Note on R^2: predictions from this method, scored against raw
        (non-demeaned) actuals, will show a HIGHER R^2 than
        `FEResult.r_squared`. That's expected, not a bug --
        `r_squared` is the *within* R^2 (fit measured on demeaned data,
        ignoring between-group variance), while scoring predict()
        against raw actuals measures the *overall* R^2, which also
        credits the model for the between-group variance fully
        captured by the recovered group intercepts. Both are valid;
        they answer different questions.

        Rows whose bank_group wasn't present in the training data raise
        a ValueError -- there's no fixed effect to use for them, and
        silently falling back to the pooled mean would understate error
        in a way that inflates apparent CV performance.
        """
        result = self.result
        preds = np.empty(len(df))
        for i, (_, row) in enumerate(df.iterrows()):
            bg = row["bank_group"]
            if bg not in result.group_intercepts:
                raise ValueError(
                    f"bank_group={bg!r} was not present in training data; "
                    "cannot predict without its fixed effect."
                )
            contribution = sum(result.coefficients[f] * row[f] for f in self.features)
            preds[i] = result.group_intercepts[bg] + contribution
        return preds

    @property
    def result(self) -> FEResult:
        if self._result is None:
            raise RuntimeError("Call .fit(df) before accessing results.")
        return self._result

    def summary(self) -> str:
        return str(self.result.model.summary())

    def _recover_group_intercepts(
        self, df: pd.DataFrame, coefficients: dict[str, float]
    ) -> dict[str, float]:
        intercepts = {}
        for bg, grp in df.groupby("bank_group"):
            y_mean = grp[self.target].mean()
            x_contribution = sum(coefficients[f] * grp[f].mean() for f in self.features)
            intercepts[bg] = y_mean - x_contribution
        return intercepts
