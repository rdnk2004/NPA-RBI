"""
Pydantic schemas for the NPA EWS API.

Kept separate from routes/api.py so the response contracts are
explicit, typed, and independently readable/testable -- not just
whatever a route handler happens to return.
"""
from __future__ import annotations

from pydantic import BaseModel, Field


class DriverRow(BaseModel):
    feature: str
    label: str
    fe_coefficient: float = Field(..., description="Fixed-effects regression coefficient")
    shap_importance: float = Field(..., description="Mean absolute SHAP value (XGBoost)")


class DriversResponse(BaseModel):
    fe_r_squared_within: float
    fe_n_obs: int
    drivers: list[DriverRow]
    note: str = (
        "Coefficients and SHAP values describe within-sample correlation "
        "structure, not validated predictive power -- see /validation."
    )


class BaselineModelResult(BaseModel):
    model: str
    mae_mean: float
    mae_std: float
    rmse_mean: float
    rmse_std: float


class ValidationResponse(BaseModel):
    n_folds: int
    fe_mae_mean: float
    fe_mae_std: float
    fe_rmse_mean: float
    fe_rmse_std: float
    baseline_comparison: list[BaselineModelResult]
    note: str = (
        "Neither the Fixed Effects model nor XGBoost meaningfully beats "
        "naive persistence at point forecasting; see baseline_comparison. "
        "This is an expected consequence of n=32, not a bug."
    )


class ReliabilityRow(BaseModel):
    bank_group: str
    n_obs: int
    year_min: int
    year_max: int
    reliable: bool


class ScenarioInfo(BaseModel):
    name: str
    description: str
    gdp_shock: float
    repo_shock: float
    credit_shock: float
    roa_shock: float


class StressRow(BaseModel):
    bank_group: str
    scenario: str
    point: float
    lower: float
    upper: float
    std: float
    breach_probability: float
    data_confidence: str


class StressResponse(BaseModel):
    threshold: float = Field(..., description="PCA Risk Threshold 1, percent GNPA")
    n_boot: int
    results: list[StressRow]


class CustomStressRequest(BaseModel):
    gdp_shock: float = Field(0.0, description="Change in GDP growth, percentage points")
    repo_shock: float = Field(0.0, description="Change in repo rate, percentage points")
    credit_shock: float = Field(0.0, description="Change in lagged credit growth, percentage points")
    roa_shock: float = Field(0.0, description="Change in ROA, percentage points")
    n_boot: int = Field(300, ge=50, le=2000, description="Bootstrap resamples (50-2000)")


class CustomStressResponse(BaseModel):
    threshold: float
    n_boot: int
    results: list[StressRow]
