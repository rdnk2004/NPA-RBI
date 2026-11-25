"""
Dynamic Panel Econometric Estimator for Bank Asset Quality.

Addresses:
1. Persistence of Non-Performing Assets: Models GNPA with lagged dependent variable (alpha).
2. Nickell Dynamic Panel Bias: Implements both Dynamic Panel Estimation (Anderson-Hsiao/Arellano-Bond
   instrumental variable first-differencing) and Fixed Effects PanelOLS with clustered entity standard errors.
3. Macro-Micro Elasticities: Quantifies the marginal impact of Return on Assets (ROA),
   Credit Growth (t-2), Credit-Deposit Ratio, Provision Coverage Ratio (PCR), and Macroeconomic cycles.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS
from linearmodels.iv import IV2SLS

from npa_ews import config

@dataclass
class DynamicPanelResult:
    params: dict[str, float]
    pvalues: dict[str, float]
    tstats: dict[str, float]
    lag_persistence: float
    r_squared: float
    n_obs: int
    n_entities: int
    model_summary: str
    is_dynamic: bool = True
    std_errors: dict[str, float] = field(default_factory=dict)

class DynamicPanelEstimator:
    """Estimates Dynamic and Static Panel models for bank asset quality."""

    def __init__(
        self,
        features: list[str] | None = None,
        target: str = "gnpa_ratio",
        entity_col: str = "bank_clean",
        time_col: str = "year"
    ):
        self.features = features or ["roa", "credit_growth_lag2", "cd_ratio", "pcr", "gdp_growth", "repo_rate"]
        self.target = target
        self.entity_col = entity_col
        self.time_col = time_col
        self._dynamic_res: DynamicPanelResult | None = None
        self._static_res: DynamicPanelResult | None = None
        self._fd_iv_res: DynamicPanelResult | None = None

    def fit(self, df: pd.DataFrame) -> DynamicPanelResult:
        """Fit dynamic panel model with lagged dependent variable and entity clustering."""
        panel_df = df.copy()
        panel_df = panel_df.sort_values([self.entity_col, self.time_col]).reset_index(drop=True)
        
        # Construct lag of target
        lag_target = f"{self.target}_lag1"
        panel_df[lag_target] = panel_df.groupby(self.entity_col)[self.target].shift(1)
        
        cols = [self.target, lag_target] + self.features
        clean = panel_df.dropna(subset=cols).copy()
        clean = clean.set_index([self.entity_col, self.time_col])

        y = clean[self.target]
        X = clean[[lag_target] + self.features]

        # PanelOLS with entity effects and cluster-robust standard errors
        model = PanelOLS(y, X, entity_effects=True)
        fitted = model.fit(cov_type="clustered", cluster_entity=True)

        params = fitted.params.to_dict()
        pvals = fitted.pvalues.to_dict()
        tstats = fitted.tstats.to_dict()
        std_errs = fitted.std_errors.to_dict()

        self._dynamic_res = DynamicPanelResult(
            params=params,
            pvalues=pvals,
            tstats=tstats,
            lag_persistence=float(params.get(lag_target, 0.0)),
            r_squared=float(fitted.rsquared_within),
            n_obs=int(fitted.nobs),
            n_entities=int(fitted.entity_info.total),
            model_summary=str(fitted.summary),
            is_dynamic=True,
            std_errors=std_errs,
        )
        return self._dynamic_res

    def fit_static(self, df: pd.DataFrame) -> DynamicPanelResult:
        """Fit static Fixed Effects benchmark without lagged dependent variable."""
        panel_df = df.copy()
        panel_df = panel_df.sort_values([self.entity_col, self.time_col]).reset_index(drop=True)
        
        cols = [self.target] + self.features
        clean = panel_df.dropna(subset=cols).copy()
        clean = clean.set_index([self.entity_col, self.time_col])

        y = clean[self.target]
        X = clean[self.features]

        model = PanelOLS(y, X, entity_effects=True)
        fitted = model.fit(cov_type="clustered", cluster_entity=True)

        params = fitted.params.to_dict()
        pvals = fitted.pvalues.to_dict()
        tstats = fitted.tstats.to_dict()
        std_errs = fitted.std_errors.to_dict()

        self._static_res = DynamicPanelResult(
            params=params,
            pvalues=pvals,
            tstats=tstats,
            lag_persistence=0.0,
            r_squared=float(fitted.rsquared_within),
            n_obs=int(fitted.nobs),
            n_entities=int(fitted.entity_info.total),
            model_summary=str(fitted.summary),
            is_dynamic=False,
            std_errors=std_errs,
        )
        return self._static_res

    def fit_fd_iv(self, df: pd.DataFrame) -> DynamicPanelResult:
        """Fit Anderson-Hsiao First-Difference IV estimator using IV2SLS.

        Eliminates entity fixed effects via consecutive-year first-differencing
        and instruments d_target_lag1 with twice-lagged level target_lag2.
        """
        panel_df = df.copy()
        panel_df = panel_df.sort_values([self.entity_col, self.time_col]).reset_index(drop=True)

        lag1_col = f"{self.target}_lag1"
        lag2_col = f"{self.target}_lag2"
        panel_df["year_diff"] = panel_df.groupby(self.entity_col)[self.time_col].diff()
        panel_df["year_lag1_diff"] = panel_df.groupby(self.entity_col)["year_diff"].shift(1)
        panel_df[lag1_col] = panel_df.groupby(self.entity_col)[self.target].shift(1)
        panel_df[lag2_col] = panel_df.groupby(self.entity_col)[self.target].shift(2)

        for col in [self.target, lag1_col] + self.features:
            panel_df[f"d_{col}"] = panel_df.groupby(self.entity_col)[col].diff()

        exog_cols = [f"d_{f}" for f in self.features]
        req = [f"d_{self.target}", f"d_{lag1_col}", lag2_col] + exog_cols
        iv_df = panel_df[
            (panel_df["year_diff"] == 1) & (panel_df["year_lag1_diff"] == 1)
        ].dropna(subset=req).copy()

        fitted = IV2SLS(
            dependent=iv_df[f"d_{self.target}"],
            exog=iv_df[exog_cols],
            endog=iv_df[[f"d_{lag1_col}"]],
            instruments=iv_df[[lag2_col]],
        ).fit(cov_type="clustered", clusters=iv_df[self.entity_col])

        # Map differenced parameter names back to canonical feature names
        raw_params = fitted.params.to_dict()
        raw_pvals = fitted.pvalues.to_dict()
        raw_tstats = fitted.tstats.to_dict()
        raw_se = fitted.std_errors.to_dict()

        def strip_d(k: str) -> str:
            return k[2:] if k.startswith("d_") else k

        params = {strip_d(k): float(v) for k, v in raw_params.items()}
        pvals = {strip_d(k): float(v) for k, v in raw_pvals.items()}
        tstats = {strip_d(k): float(v) for k, v in raw_tstats.items()}
        std_errs = {strip_d(k): float(v) for k, v in raw_se.items()}

        self._fd_iv_res = DynamicPanelResult(
            params=params,
            pvalues=pvals,
            tstats=tstats,
            lag_persistence=float(params.get(lag1_col, 0.0)),
            r_squared=float(fitted.rsquared),
            n_obs=int(fitted.nobs),
            n_entities=int(iv_df[self.entity_col].nunique()),
            model_summary=str(fitted.summary),
            is_dynamic=True,
            std_errors=std_errs,
        )
        return self._fd_iv_res

    def compare_static_vs_dynamic(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate side-by-side comparison across Static FE, Dynamic FE, and Anderson-Hsiao FD-IV."""
        if self._dynamic_res is None:
            self.fit(df)
        if self._static_res is None:
            self.fit_static(df)
        if self._fd_iv_res is None:
            self.fit_fd_iv(df)

        comparison = []
        all_vars = [f"{self.target}_lag1"] + self.features
        for var in all_vars:
            stat_val = self._static_res.params.get(var)
            stat_p = self._static_res.pvalues.get(var)
            dyn_val = self._dynamic_res.params.get(var)
            dyn_p = self._dynamic_res.pvalues.get(var)
            iv_val = self._fd_iv_res.params.get(var)
            iv_p = self._fd_iv_res.pvalues.get(var)

            def fmt(coef, p):
                if coef is None:
                    return "-"
                stars = "***" if p < 0.01 else ("**" if p < 0.05 else ("*" if p < 0.1 else ""))
                return f"{coef:.4f}{stars} (p={p:.3f})"

            comparison.append({
                "Variable": var,
                "Static Fixed Effects": fmt(stat_val, stat_p),
                "Dynamic FE (LSDV)": fmt(dyn_val, dyn_p),
                "Dynamic Panel (IV/FD)": fmt(iv_val, iv_p),
            })

        table = pd.DataFrame(comparison).set_index("Variable")
        return table
