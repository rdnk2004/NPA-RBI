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


def validate_bank_level_models(
    bank_df: pd.DataFrame,
    features: list[str] | None = None,
    split_year: int = 2021,
) -> dict[str, pd.DataFrame]:
    """Evaluate continuous and PCA-breach classification models on bank-level panel.

    Splits temporally at split_year (e.g. Train <= 2021, Test >= 2022) to avoid lookahead.
    """
    from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import (
        accuracy_score,
        f1_score,
        mean_absolute_error,
        mean_squared_error,
        precision_score,
        r2_score,
        recall_score,
        roc_auc_score,
    )
    from npa_ews.models.xgb_model import GnpaXGBModel, PcaBreachClassifier

    feats = features or config.BANK_LEVEL_FEATURES
    clean = bank_df.dropna(subset=feats + ["gnpa_next1yr", "pca_breach_next1yr"]).copy()

    train = clean[clean["year"] <= split_year]
    test = clean[clean["year"] > split_year]

    if train.empty or test.empty:
        raise ValueError(f"Insufficient train ({len(train)}) or test ({len(test)}) observations.")

    # 1. Regression Comparison
    y_test_reg = test["gnpa_next1yr"].to_numpy()
    naive_preds = test["gnpa_ratio"].to_numpy()

    xgb_reg = GnpaXGBModel(features=feats, target="gnpa_next1yr").fit(train, test)
    xgb_preds = xgb_reg.predict(test)

    rf_reg = RandomForestRegressor(n_estimators=100, max_depth=5, random_state=config.RANDOM_SEED)
    rf_reg.fit(train[feats], train["gnpa_next1yr"])
    rf_preds = rf_reg.predict(test[feats])

    reg_summary = pd.DataFrame([
        {
            "Model": "Naive (persistence: gnpa_t)",
            "MAE": round(mean_absolute_error(y_test_reg, naive_preds), 3),
            "RMSE": round(float(np.sqrt(mean_squared_error(y_test_reg, naive_preds))), 3),
            "R2": round(r2_score(y_test_reg, naive_preds), 3),
        },
        {
            "Model": "Random Forest Regressor",
            "MAE": round(mean_absolute_error(y_test_reg, rf_preds), 3),
            "RMSE": round(float(np.sqrt(mean_squared_error(y_test_reg, rf_preds))), 3),
            "R2": round(r2_score(y_test_reg, rf_preds), 3),
        },
        {
            "Model": "XGBoost Regressor",
            "MAE": round(mean_absolute_error(y_test_reg, xgb_preds), 3),
            "RMSE": round(float(np.sqrt(mean_squared_error(y_test_reg, xgb_preds))), 3),
            "R2": round(r2_score(y_test_reg, xgb_preds), 3),
        },
    ]).set_index("Model")

    # 2. PCA Breach Classification Comparison
    y_test_cls = test["pca_breach_next1yr"].astype(int).to_numpy()

    # Logit baseline
    logit = LogisticRegression(max_iter=1000, random_state=config.RANDOM_SEED)
    logit.fit(train[feats], train["pca_breach_next1yr"].astype(int))
    logit_probs = logit.predict_proba(test[feats])[:, 1]
    logit_preds = (logit_probs >= 0.5).astype(int)

    # Random Forest
    rf_cls = RandomForestClassifier(n_estimators=100, max_depth=4, random_state=config.RANDOM_SEED)
    rf_cls.fit(train[feats], train["pca_breach_next1yr"].astype(int))
    rf_probs = rf_cls.predict_proba(test[feats])[:, 1]
    rf_preds = (rf_probs >= 0.5).astype(int)

    # XGBoost
    xgb_cls = PcaBreachClassifier(features=feats, target="pca_breach_next1yr").fit(train)
    xgb_probs = xgb_cls.predict_proba(test)
    xgb_preds_cls = (xgb_probs >= 0.5).astype(int)

    def calc_cls_metrics(y_true, probs, preds):
        return {
            "ROC_AUC": round(float(roc_auc_score(y_true, probs)), 3),
            "Accuracy": round(float(accuracy_score(y_true, preds)), 3),
            "Precision": round(float(precision_score(y_true, preds, zero_division=0)), 3),
            "Recall": round(float(recall_score(y_true, preds, zero_division=0)), 3),
            "F1_Score": round(float(f1_score(y_true, preds, zero_division=0)), 3),
        }

    cls_summary = pd.DataFrame([
        {"Model": "Logistic Regression (Logit)", **calc_cls_metrics(y_test_cls, logit_probs, logit_preds)},
        {"Model": "Random Forest Classifier", **calc_cls_metrics(y_test_cls, rf_probs, rf_preds)},
        {"Model": "XGBoost Classifier", **calc_cls_metrics(y_test_cls, xgb_probs, xgb_preds_cls)},
    ]).set_index("Model")

    return {
        "regression": reg_summary,
        "classification": cls_summary,
        "n_train": len(train),
        "n_test": len(test),
    }



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
