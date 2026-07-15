"""
Central configuration for the NPA Early Warning System.

Every notebook/script in the original repo redefined FEATURES, TARGET,
DATA/OUTPUTS paths, and GROUP_COLORS independently. That's a
maintenance hazard: change a feature list in one place, silently break
another. This module is the single source of truth.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────
# Resolved relative to the package location, NOT the current working
# directory — the original scripts used "../datasets/" which only
# worked if you happened to run them from notebooks/.
ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "datasets"
OUTPUTS_DIR = ROOT_DIR / "outputs"
POLICY_DIR = ROOT_DIR / "policy_note"

BANKING_PANEL_CSV = DATA_DIR / "banking_panel.csv"
MACRO_ANNUAL_CSV = DATA_DIR / "macro_annual.csv"

# ── Modeling ─────────────────────────────────────────────────────────
FEATURES: list[str] = [
    "credit_growth_lag2",
    "roa",
    "pcr",
    "gdp_growth",
    "repo_rate",
    "cpi_avg",
]

TARGET: str = "gnpa_next1yr"

FEATURE_LABELS: dict[str, str] = {
    "credit_growth_lag2": "Credit Growth (t-2)",
    "roa": "Return on Assets",
    "pcr": "Provision Coverage Ratio",
    "gdp_growth": "GDP Growth",
    "repo_rate": "Repo Rate",
    "cpi_avg": "CPI Inflation",
}

# Last year with full actuals in the panel; anything beyond this is
# forecast/derived, not observed.
MAX_ACTUAL_YEAR = 2025

# Temporal split boundary used for the holdout test set.
TRAIN_YEAR_MAX = 2021
TEST_YEAR_MIN = 2022

GROUP_COLORS: dict[str, str] = {
    "PSB": "#e74c3c",
    "Private": "#3498db",
    "Foreign": "#27ae60",
    "SFB": "#f39c12",
}

BANK_GROUPS: list[str] = list(GROUP_COLORS.keys())

# RBI Prompt Corrective Action GNPA thresholds (traffic-light signal).
TRAFFIC_LIGHT_THRESHOLDS: dict[str, float] = {
    "HIGH ALERT": 7.0,
    "WATCH": 5.0,
    "ELEVATED": 3.0,
    # below ELEVATED -> "NORMAL"
}


@dataclass(frozen=True)
class StressScenario:
    name: str
    description: str
    gdp_shock: float = 0.0
    repo_shock: float = 0.0
    credit_shock: float = 0.0
    roa_shock: float = 0.0


STRESS_SCENARIOS: list[StressScenario] = [
    StressScenario(
        name="Baseline (2024 actuals)",
        description="No change from 2024",
    ),
    StressScenario(
        name="Mild Stress (IL&FS 2019)",
        description="IL&FS-type liquidity crunch",
        gdp_shock=-1.5,
        repo_shock=0.5,
        credit_shock=-3.0,
        roa_shock=-0.15,
    ),
    StressScenario(
        name="Severe Stress (Post-AQR 2017)",
        description="Post-AQR recognition shock",
        gdp_shock=-2.5,
        repo_shock=1.0,
        credit_shock=-6.0,
        roa_shock=-0.40,
    ),
    StressScenario(
        name="Tail Risk (COVID FY21)",
        description="COVID-FY21 tail risk scenario (GDP 8.2% to -4.3%)",
        gdp_shock=-12.5,
        repo_shock=-1.0,
        credit_shock=-8.0,
        roa_shock=-0.80,
    ),
]

RANDOM_SEED = 42
