"""
Data loading and validation for the NPA EWS pipeline.

The original notebooks did `pd.read_csv(...)` and trusted the file.
That's fine for a one-off analysis; it's not fine for anything you'd
call "engineered". This module fails loudly, with a specific message,
the moment the panel doesn't look like what the models expect --
before a bad merge or a schema drift silently corrupts a regression.
"""
from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from npa_ews import config

logger = logging.getLogger(__name__)

REQUIRED_COLUMNS: set[str] = {
    "year",
    "bank_group",
    "gnpa_ratio",
    *config.FEATURES,
    config.TARGET,
}


class SchemaError(ValueError):
    """Raised when the panel dataset doesn't match the expected schema."""


def load_banking_panel(
    path: Path = config.BANKING_PANEL_CSV,
    *,
    max_year: int = config.MAX_ACTUAL_YEAR,
    validate: bool = True,
) -> pd.DataFrame:
    """Load the bank-group x year panel dataset.

    Parameters
    ----------
    path:
        CSV location. Defaults to the repo's datasets/banking_panel.csv.
    max_year:
        Rows beyond this year are dropped (matches original notebooks'
        `panel[panel['year'] <= 2025]` filter).
    validate:
        If True (default), run schema + sanity checks and raise
        SchemaError on failure rather than silently proceeding.
    """
    if not path.exists():
        raise FileNotFoundError(
            f"Banking panel not found at {path}. "
            "Run from the repo root or pass an explicit path."
        )

    df = pd.read_csv(path)

    if validate:
        _validate_schema(df, path)

    df = df[df["year"] <= max_year].copy()
    df = df.sort_values(["bank_group", "year"]).reset_index(drop=True)

    logger.info(
        "Loaded banking panel: %d rows, %d bank groups, years %d-%d",
        len(df),
        df["bank_group"].nunique(),
        df["year"].min(),
        df["year"].max(),
    )
    return df


def load_macro_annual(path: Path = config.MACRO_ANNUAL_CSV) -> pd.DataFrame:
    """Load the standalone macroeconomic time series (GDP, repo, CPI, IIP)."""
    if not path.exists():
        raise FileNotFoundError(f"Macro annual file not found at {path}.")
    return pd.read_csv(path).sort_values("year").reset_index(drop=True)


def get_model_ready_frame(panel: pd.DataFrame) -> pd.DataFrame:
    """Drop rows with any missing feature or target -- the exact frame
    every model in this repo trains on. Centralizing this means the
    panel regression, XGBoost, and stress test can no longer silently
    diverge on *which* rows count as "usable"."""
    ml_df = panel.dropna(subset=config.FEATURES + [config.TARGET]).copy()
    return ml_df.sort_values(["bank_group", "year"]).reset_index(drop=True)


def group_reliability(ml_df: pd.DataFrame, min_obs: int = config.MIN_RELIABLE_OBS) -> pd.DataFrame:
    """Per-bank_group observation counts and a reliability flag.

    Returns a DataFrame indexed by bank_group with columns
    [n_obs, year_min, year_max, reliable]. `reliable` is False when
    n_obs < min_obs -- meaning any fixed effect, prediction, or
    confidence interval for that group rests on too little data to
    trust at face value, regardless of which model produced it.

    This exists because two of this dataset's four bank groups (PSB,
    SFB) only have data from 2018 onward in the source RBI/government
    tables, vs. 2004+ for Foreign/Private -- a real, permanent gap in
    the underlying data, not something more feature engineering or a
    different model can fix.
    """
    summary = (
        ml_df.groupby("bank_group")["year"]
        .agg(n_obs="count", year_min="min", year_max="max")
        .reindex(config.BANK_GROUPS)
    )
    summary["reliable"] = summary["n_obs"] >= min_obs
    return summary


def annotate_reliability(
    df: pd.DataFrame, reliability: pd.DataFrame, group_col: str = "bank_group"
) -> pd.DataFrame:
    """Attach a human-readable reliability caveat column to any
    DataFrame indexed or keyed by bank_group (e.g. a stress test or
    bootstrap CI table), so the flag travels with the number instead
    of living only in a separate report."""
    out = df.copy()
    is_index = out.index.name == group_col or (
        out.index.name is None and set(out.index) <= set(config.BANK_GROUPS)
    )
    keys = out.index if is_index else out[group_col]
    caveats = []
    for key in keys:
        n = reliability.loc[key, "n_obs"] if key in reliability.index else None
        if n is None or pd.isna(n):
            caveats.append("no data")
        elif n < config.MIN_RELIABLE_OBS:
            caveats.append(f"LOW CONFIDENCE (n={int(n)})")
        else:
            caveats.append(f"reliable (n={int(n)})")
    out["data_confidence"] = caveats
    return out


def _validate_schema(df: pd.DataFrame, source: Path) -> None:
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise SchemaError(
            f"{source.name} is missing required columns: {sorted(missing)}"
        )

    unknown_groups = set(df["bank_group"].dropna().unique()) - set(config.BANK_GROUPS)
    if unknown_groups:
        raise SchemaError(
            f"{source.name} contains unexpected bank_group values: "
            f"{sorted(unknown_groups)}. Expected one of {config.BANK_GROUPS}."
        )

    if df["gnpa_ratio"].dropna().lt(0).any():
        raise SchemaError(f"{source.name} contains negative gnpa_ratio values.")

    if df["gnpa_ratio"].dropna().gt(50).any():
        # GNPA ratios above 50% are implausible for any real bank group
        # and almost always indicate a unit error (e.g. not-yet-divided
        # by 100, or a bad merge). This is a sanity check, not a hard
        # business rule -- raise so a human looks at it.
        raise SchemaError(
            f"{source.name} contains gnpa_ratio > 50%, which is implausible. "
            "Check for a unit or merge error."
        )

    dupes = df.duplicated(subset=["year", "bank_group"]).sum()
    if dupes:
        raise SchemaError(
            f"{source.name} has {dupes} duplicate (year, bank_group) rows."
        )
