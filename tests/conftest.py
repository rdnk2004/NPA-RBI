import warnings

import numpy as np
import pandas as pd
import pytest

from npa_ews import config

# Fires at import time (starlette.testclient importing httpx), before
# pytest's [tool.pytest.ini_options] filterwarnings takes effect for
# collection-time warnings -- suppressed here instead so it doesn't
# show up in every test run's warning summary.
warnings.filterwarnings(
    "ignore",
    message="Using `httpx` with `starlette.testclient` is deprecated.*",
    category=DeprecationWarning,
)


@pytest.fixture
def synthetic_panel() -> pd.DataFrame:
    """A small, deterministic panel that mimics the real schema.

    Using synthetic data (rather than the real CSV) means these tests
    keep passing even if the real dataset is later extended with more
    years or bank groups -- they test the *code's* behavior, not
    today's specific numbers.
    """
    rng = np.random.default_rng(config.RANDOM_SEED)
    rows = []
    for bg in config.BANK_GROUPS:
        base = {"PSB": 4.0, "Private": 2.0, "Foreign": 1.5, "SFB": 2.5}[bg]
        for year in range(2015, 2025):
            rows.append(
                {
                    "year": year,
                    "bank_group": bg,
                    "gnpa_ratio": max(0.1, base + rng.normal(0, 0.5)),
                    "credit_growth_lag2": 10 + rng.normal(0, 3),
                    "roa": 1.0 + rng.normal(0, 0.3),
                    "pcr": 60 + rng.normal(0, 5),
                    "gdp_growth": 6.5 + rng.normal(0, 1.5),
                    "repo_rate": 5.5 + rng.normal(0, 0.5),
                    "cpi_avg": 5.0 + rng.normal(0, 1.0),
                }
            )
    df = pd.DataFrame(rows)
    # gnpa_next1yr: shift within each bank_group
    df = df.sort_values(["bank_group", "year"])
    df["gnpa_next1yr"] = df.groupby("bank_group")["gnpa_ratio"].shift(-1)
    return df.reset_index(drop=True)


@pytest.fixture
def model_ready_panel(synthetic_panel) -> pd.DataFrame:
    from npa_ews.data import get_model_ready_frame

    return get_model_ready_frame(synthetic_panel)
