"""
Validation rigor: walk-forward (expanding-window) cross-validation.

The original notebooks fit on ONE train/test split (train <= 2021,
test >= 2022) and reported a single R^2. With n~32, that's one draw
from a noisy process -- a lucky or unlucky split changes the reported
number more than the model does. Walk-forward CV answers a different,
more honest question: "if we'd been re-fitting this model every year
as new data arrived, how consistently would it have performed?"

Each fold trains on all years up to a cutoff and tests on exactly the
next year -- never on the past, never on a year the model could have
seen. This mirrors how the model would actually be used in production
(re-fit annually as RBI's Trend & Progress report is released) and is
the correct CV scheme for the FE model, which requires all bank groups
present in training to recover group intercepts.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error

from npa_ews import config
from npa_ews.models.panel_fe import FixedEffectsRegressor
from npa_ews.models.xgb_model import GnpaXGBModel

logger = logging.getLogger(__name__)


@dataclass
class CVFold:
    train_year_range: tuple[int, int]
    test_year: int
    n_train: int
    n_test: int
    mae: float
    rmse: float


@dataclass
class WalkForwardResult:
    folds: list[CVFold]
    mean_mae: float
    std_mae: float
    mean_rmse: float
    std_rmse: float

    def summary_table(self) -> pd.DataFrame:
        return pd.DataFrame(
            [
                {
                    "train_years": f"{f.train_year_range[0]}-{f.train_year_range[1]}",
                    "test_year": f.test_year,
                    "n_train": f.n_train,
                    "n_test": f.n_test,
                    "mae": round(f.mae, 3),
                    "rmse": round(f.rmse, 3),
                }
                for f in self.folds
            ]
        )


def _naive_predict(train: pd.DataFrame, test: pd.DataFrame, target: str) -> np.ndarray:
    """Persistence baseline: predict next year's GNPA = this year's
    GNPA (i.e. gnpa_ratio), per bank_group. The bar any model must
    clear to be worth using at all."""
    return test["gnpa_ratio"].to_numpy()


def _mean_predict(train: pd.DataFrame, test: pd.DataFrame, target: str) -> np.ndarray:
    """Historical-mean baseline: predict each bank_group's own
    training-period average target, ignoring all features."""
    group_means = train.groupby("bank_group")[target].mean()
    return test["bank_group"].map(group_means).to_numpy()


def _pooled_ols_predict(
    train: pd.DataFrame, test: pd.DataFrame, features: list[str], target: str
) -> np.ndarray:
    """Plain pooled OLS: same features as the FE model, but with no
    bank_group fixed effects at all -- i.e. what you'd get if you
    ignored the panel structure entirely."""
    import statsmodels.api as sm

    X_train = sm.add_constant(train[features])
    model = sm.OLS(train[target], X_train).fit()
    X_test = sm.add_constant(test[features], has_constant="add")
    return model.predict(X_test[X_train.columns]).to_numpy()


def compare_baselines(
    ml_df: pd.DataFrame,
    features: list[str] | None = None,
    target: str | None = None,
    min_train_years: int = 5,
) -> pd.DataFrame:
    """Run naive persistence, historical mean, pooled OLS, and the
    fixed-effects model through the *same* walk-forward folds, so
    "is the fixed-effects model actually worth it" has a real,
    apples-to-apples answer instead of a single model's number sitting
    in isolation.

    A model that doesn't beat the naive/mean baselines by a meaningful
    margin isn't earning its complexity, regardless of how
    sophisticated it is -- this is the check that should happen
    *before* reaching for a fancier algorithm like XGBoost, not after.
    """
    features = features or config.FEATURES
    target = target or config.TARGET
    all_groups = set(ml_df["bank_group"].unique())
    years = sorted(ml_df["year"].unique())

    predictors = {
        "Naive (persistence)": lambda tr, te: _naive_predict(tr, te, target),
        "Historical mean": lambda tr, te: _mean_predict(tr, te, target),
        "Pooled OLS (no fixed effects)": lambda tr, te: _pooled_ols_predict(tr, te, features, target),
    }

    rows = []
    for cutoff in years[min_train_years - 1 : -1]:
        train = ml_df[ml_df["year"] <= cutoff]
        test = ml_df[ml_df["year"] == cutoff + 1]
        if not all_groups.issubset(set(train["bank_group"].unique())):
            continue
        test = test[test["bank_group"].isin(all_groups)]
        if test.empty:
            continue
        actual = test[target].to_numpy()

        for name in ("Naive (persistence)", "Historical mean", "Pooled OLS (no fixed effects)"):
            preds = predictors[name](train, test)
            rows.append(
                {
                    "model": name,
                    "test_year": cutoff + 1,
                    "mae": mean_absolute_error(actual, preds),
                    "rmse": float(np.sqrt(mean_squared_error(actual, preds))),
                }
            )

        fe = FixedEffectsRegressor(features, target)
        fe.fit(train)
        preds = fe.predict(test)
        rows.append(
            {
                "model": "Fixed Effects",
                "test_year": cutoff + 1,
                "mae": mean_absolute_error(actual, preds),
                "rmse": float(np.sqrt(mean_squared_error(actual, preds))),
            }
        )

        xgb_model = GnpaXGBModel(features, target).fit(train, test)
        xgb_preds = xgb_model.predict(test)
        rows.append(
            {
                "model": "XGBoost",
                "test_year": cutoff + 1,
                "mae": mean_absolute_error(actual, xgb_preds),
                "rmse": float(np.sqrt(mean_squared_error(actual, xgb_preds))),
            }
        )

    if not rows:
        raise ValueError("No valid folds produced for baseline comparison.")

    detail = pd.DataFrame(rows)
    summary = (
        detail.groupby("model")[["mae", "rmse"]]
        .agg(["mean", "std"])
        .round(3)
    )
    summary.columns = ["_".join(c) for c in summary.columns]
    order = [
        "Naive (persistence)",
        "Historical mean",
        "Pooled OLS (no fixed effects)",
        "Fixed Effects",
        "XGBoost",
    ]
    return summary.reindex(order)


def walk_forward_cv(
    ml_df: pd.DataFrame,
    features: list[str] | None = None,
    target: str | None = None,
    min_train_years: int = 5,
) -> WalkForwardResult:
    """Expanding-window CV for the fixed-effects model.

    Parameters
    ----------
    ml_df:
        Model-ready panel (output of data.get_model_ready_frame).
    min_train_years:
        Minimum number of distinct years required before the first
        fold is evaluated. With very few years, an early fold's FE
        model is fit on too little within-group variation to mean
        much -- this floor keeps folds meaningful rather than just
        maximizing fold count.

    Raises
    ------
    ValueError if no valid folds could be constructed (e.g. dataset
    has fewer years than min_train_years + 1, or every test year's
    bank groups are absent from training).
    """
    features = features or config.FEATURES
    target = target or config.TARGET
    all_groups = set(ml_df["bank_group"].unique())
    years = sorted(ml_df["year"].unique())

    if len(years) < min_train_years + 1:
        raise ValueError(
            f"Only {len(years)} distinct years available; need at least "
            f"{min_train_years + 1} for min_train_years={min_train_years}."
        )

    folds: list[CVFold] = []
    for cutoff in years[min_train_years - 1 : -1]:
        train = ml_df[ml_df["year"] <= cutoff]
        test = ml_df[ml_df["year"] == cutoff + 1]

        # FE prediction requires every test-row bank_group to have been
        # seen in training; skip folds where that's not the case rather
        # than silently dropping rows and misreporting fold size.
        if not all_groups.issubset(set(train["bank_group"].unique())):
            logger.debug("Skipping fold at cutoff=%d: not all groups in training.", cutoff)
            continue
        test = test[test["bank_group"].isin(all_groups)]
        if test.empty:
            continue

        fe = FixedEffectsRegressor(features, target)
        fe.fit(train)
        preds = fe.predict(test)
        actual = test[target].to_numpy()

        folds.append(
            CVFold(
                train_year_range=(int(train["year"].min()), int(train["year"].max())),
                test_year=int(cutoff + 1),
                n_train=len(train),
                n_test=len(test),
                mae=mean_absolute_error(actual, preds),
                rmse=float(np.sqrt(mean_squared_error(actual, preds))),
            )
        )

    if not folds:
        raise ValueError(
            "No valid CV folds produced. Check that every year has all "
            "bank groups present, and that min_train_years leaves at "
            "least one test year."
        )

    maes = [f.mae for f in folds]
    rmses = [f.rmse for f in folds]
    return WalkForwardResult(
        folds=folds,
        mean_mae=float(np.mean(maes)),
        std_mae=float(np.std(maes)),
        mean_rmse=float(np.mean(rmses)),
        std_rmse=float(np.std(rmses)),
    )
