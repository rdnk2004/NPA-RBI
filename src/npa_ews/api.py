"""
FastAPI serving layer for the NPA EWS.

Design choices:
- Models (FE, XGBoost) and expensive computations (walk-forward CV,
  baseline comparison) are fitted ONCE at startup via FastAPI's
  lifespan handler and cached on app.state, not recomputed per
  request. The 32-row dataset makes this fast, but the pattern is the
  right one regardless of dataset size.
- Every response is a typed Pydantic model (schemas.py) -- the
  contract is explicit and shows up correctly in the auto-generated
  /docs, rather than routes returning ad-hoc dicts.
- Every numeric table (drivers, stress results) carries the same
  interpretive caveats as the README/policy note (data_confidence,
  the naive-baseline note) -- the API can't be used in a way that
  drops the honesty the rest of this project insists on.

Run with: uvicorn npa_ews.api:app --reload
Docs at:  http://127.0.0.1:8000/docs
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from dataclasses import dataclass

import pandas as pd
from fastapi import FastAPI, HTTPException

from npa_ews import __version__, config, data, stress, validation
from npa_ews.models import FixedEffectsRegressor, GnpaXGBModel
from npa_ews.schemas import (
    BaselineModelResult,
    CustomStressRequest,
    CustomStressResponse,
    DriverRow,
    DriversResponse,
    ReliabilityRow,
    ScenarioInfo,
    StressResponse,
    StressRow,
    ValidationResponse,
)

logger = logging.getLogger("npa_ews.api")


@dataclass
class AppState:
    panel: pd.DataFrame
    ml_df: pd.DataFrame
    fe: FixedEffectsRegressor
    xgb_model: GnpaXGBModel
    reliability: pd.DataFrame
    baseline: pd.DataFrame
    validation_result: validation.WalkForwardResult
    baseline_comparison: pd.DataFrame


state: AppState | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global state
    logger.info("Loading data and fitting models (once, at startup)...")
    panel = data.load_banking_panel()
    ml_df = data.get_model_ready_frame(panel)

    fe = FixedEffectsRegressor()
    fe.fit(ml_df)

    train = ml_df[ml_df["year"] <= config.TRAIN_YEAR_MAX]
    test = ml_df[ml_df["year"] >= config.TEST_YEAR_MIN]
    xgb_model = GnpaXGBModel().fit(train, test)

    reliability = data.group_reliability(ml_df)
    baseline_df = panel[panel["year"] == 2024].dropna(subset=config.FEATURES).set_index("bank_group")

    validation_result = validation.walk_forward_cv(ml_df)
    baseline_comparison = validation.compare_baselines(ml_df)

    state = AppState(
        panel=panel,
        ml_df=ml_df,
        fe=fe,
        xgb_model=xgb_model,
        reliability=reliability,
        baseline=baseline_df,
        validation_result=validation_result,
        baseline_comparison=baseline_comparison,
    )
    logger.info("Startup complete: FE R^2=%.3f, %d CV folds.", fe.result.r_squared, len(validation_result.folds))
    yield
    state = None


app = FastAPI(
    title="NPA Early Warning System API",
    description=(
        "SupTech prototype: bank-group NPA driver identification, out-of-sample "
        "validation, and probabilistic macro stress testing for Indian banking "
        "supervision. Read /drivers and /validation together -- this system's "
        "value is driver identification and scenario risk, not point forecasting."
    ),
    version=__version__,
    lifespan=lifespan,
)


def _get_state() -> AppState:
    if state is None:
        raise HTTPException(status_code=503, detail="Models not yet loaded.")
    return state


@app.get("/", tags=["meta"])
def root() -> dict:
    return {
        "name": "NPA Early Warning System API",
        "version": __version__,
        "docs": "/docs",
        "endpoints": ["/health", "/drivers", "/validation", "/reliability", "/scenarios", "/stress", "/stress/custom"],
    }


@app.get("/health", tags=["meta"])
def health() -> dict:
    return {"status": "ok" if state is not None else "loading"}


@app.get("/drivers", response_model=DriversResponse, tags=["findings"])
def get_drivers() -> DriversResponse:
    """Fixed-effects coefficients and SHAP global importance, side by
    side -- two independent methods' answer to "what moves GNPA?"."""
    s = _get_state()
    shap_importance = s.xgb_model.global_importance(s.ml_df)
    rows = [
        DriverRow(
            feature=f,
            label=config.FEATURE_LABELS.get(f, f),
            fe_coefficient=round(s.fe.result.coefficients[f], 4),
            shap_importance=round(float(shap_importance.get(f, 0.0)), 4),
        )
        for f in config.FEATURES
    ]
    return DriversResponse(
        fe_r_squared_within=round(s.fe.result.r_squared, 4),
        fe_n_obs=s.fe.result.n_obs,
        drivers=rows,
    )


@app.get("/validation", response_model=ValidationResponse, tags=["findings"])
def get_validation() -> ValidationResponse:
    """Walk-forward CV performance plus the naive/mean/OLS/XGBoost
    baseline comparison -- the honest answer to "is this worth it?"."""
    s = _get_state()
    vr = s.validation_result
    comparison = [
        BaselineModelResult(
            model=model_name,
            mae_mean=row["mae_mean"],
            mae_std=row["mae_std"],
            rmse_mean=row["rmse_mean"],
            rmse_std=row["rmse_std"],
        )
        for model_name, row in s.baseline_comparison.iterrows()
    ]
    return ValidationResponse(
        n_folds=len(vr.folds),
        fe_mae_mean=round(vr.mean_mae, 4),
        fe_mae_std=round(vr.std_mae, 4),
        fe_rmse_mean=round(vr.mean_rmse, 4),
        fe_rmse_std=round(vr.std_rmse, 4),
        baseline_comparison=comparison,
    )


@app.get("/reliability", response_model=list[ReliabilityRow], tags=["findings"])
def get_reliability() -> list[ReliabilityRow]:
    """Per-bank-group observation counts and the low-confidence flag
    (e.g. PSB/SFB at n=4) that every stress result also carries."""
    s = _get_state()
    return [
        ReliabilityRow(
            bank_group=bg,
            n_obs=int(row["n_obs"]),
            year_min=int(row["year_min"]),
            year_max=int(row["year_max"]),
            reliable=bool(row["reliable"]),
        )
        for bg, row in s.reliability.iterrows()
    ]


@app.get("/scenarios", response_model=list[ScenarioInfo], tags=["stress"])
def get_scenarios() -> list[ScenarioInfo]:
    """The predefined macro stress scenarios (calibrated to IL&FS 2019,
    Post-AQR 2017, and COVID FY21)."""
    return [
        ScenarioInfo(
            name=sc.name,
            description=sc.description,
            gdp_shock=sc.gdp_shock,
            repo_shock=sc.repo_shock,
            credit_shock=sc.credit_shock,
            roa_shock=sc.roa_shock,
        )
        for sc in config.STRESS_SCENARIOS
    ]


@app.get("/stress", response_model=StressResponse, tags=["stress"])
def get_stress(n_boot: int = 300) -> StressResponse:
    """Bootstrap-CI stress test results for every predefined scenario
    and bank group, each carrying its data-reliability flag.

    n_boot: bootstrap resamples (default 300; capped at 2000 to keep
    response times reasonable for an interactive API).
    """
    if not 50 <= n_boot <= 2000:
        raise HTTPException(status_code=400, detail="n_boot must be between 50 and 2000.")
    s = _get_state()
    boot_results = stress.bootstrap_stress_test(s.ml_df, s.baseline, n_boot=n_boot)

    rows: list[StressRow] = []
    for scenario_name, scenario_df in boot_results.items():
        annotated = data.annotate_reliability(scenario_df, s.reliability)
        for bg, row in annotated.iterrows():
            rows.append(
                StressRow(
                    bank_group=bg,
                    scenario=scenario_name,
                    point=row["point"],
                    lower=row["lower"],
                    upper=row["upper"],
                    std=row["std"],
                    breach_probability=row["breach_prob"],
                    data_confidence=row["data_confidence"],
                )
            )
    return StressResponse(threshold=stress.PCA_THRESHOLD_1, n_boot=n_boot, results=rows)


@app.post("/stress/custom", response_model=CustomStressResponse, tags=["stress"])
def post_custom_stress(req: CustomStressRequest) -> CustomStressResponse:
    """Run the bootstrap stress test for a user-defined macro shock,
    not just the three predefined historical scenarios -- e.g. "what
    if GDP growth falls 3pp and the repo rate rises 1pp?"."""
    s = _get_state()
    custom_scenario = config.StressScenario(
        name="Custom",
        description="User-defined scenario",
        gdp_shock=req.gdp_shock,
        repo_shock=req.repo_shock,
        credit_shock=req.credit_shock,
        roa_shock=req.roa_shock,
    )
    boot_results = stress.bootstrap_stress_test(
        s.ml_df, s.baseline, scenarios=[custom_scenario], n_boot=req.n_boot
    )
    scenario_df = boot_results["Custom"]
    annotated = data.annotate_reliability(scenario_df, s.reliability)

    rows = [
        StressRow(
            bank_group=bg,
            scenario="Custom",
            point=row["point"],
            lower=row["lower"],
            upper=row["upper"],
            std=row["std"],
            breach_probability=row["breach_prob"],
            data_confidence=row["data_confidence"],
        )
        for bg, row in annotated.iterrows()
    ]
    return CustomStressResponse(threshold=stress.PCA_THRESHOLD_1, n_boot=req.n_boot, results=rows)
