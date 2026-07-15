"""
XGBoost regressor + SHAP explainability, wrapped as a reusable class.

Extracted from 04_xgboost_shap.py. Hyperparameters are intentionally
conservative (max_depth=2, strong regularization) -- see the docstring
on GnpaXGBModel for why, given n~32.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
import shap
import xgboost as xgb
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from npa_ews import config


@dataclass
class EvalMetrics:
    train_r2: float
    test_r2: float
    test_rmse: float
    test_mae: float


class GnpaXGBModel:
    """Shallow, regularized XGBoost regressor for next-year GNPA.

    Design rationale (kept from the original notebook, now enforced in
    code rather than just comments): with ~32 training rows, a deep or
    unregularized tree ensemble memorizes noise. max_depth=2 and
    min_child_weight=3 force the model to find only the strongest,
    most repeated patterns -- consistent with using it as a
    *pattern-identifier*, not a precision forecaster.
    """

    def __init__(
        self,
        features: list[str] | None = None,
        target: str | None = None,
        **xgb_kwargs,
    ):
        self.features = features or config.FEATURES
        self.target = target or config.TARGET
        params = dict(
            n_estimators=100,
            max_depth=2,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            min_child_weight=3,
            reg_alpha=0.5,
            reg_lambda=1.0,
            random_state=config.RANDOM_SEED,
            verbosity=0,
        )
        params.update(xgb_kwargs)
        self.model = xgb.XGBRegressor(**params)
        self._explainer: shap.TreeExplainer | None = None
        self._fitted = False

    def fit(self, train_df: pd.DataFrame, test_df: pd.DataFrame | None = None) -> "GnpaXGBModel":
        X_train, y_train = train_df[self.features], train_df[self.target]
        eval_set = None
        if test_df is not None:
            eval_set = [(test_df[self.features], test_df[self.target])]
        self.model.fit(X_train, y_train, eval_set=eval_set, verbose=False)
        self._explainer = shap.TreeExplainer(self.model)
        self._fitted = True
        return self

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        self._check_fitted()
        return self.model.predict(df[self.features])

    def evaluate(self, train_df: pd.DataFrame, test_df: pd.DataFrame) -> EvalMetrics:
        self._check_fitted()
        y_train_pred = self.predict(train_df)
        y_test_pred = self.predict(test_df)
        return EvalMetrics(
            train_r2=r2_score(train_df[self.target], y_train_pred),
            test_r2=r2_score(test_df[self.target], y_test_pred),
            test_rmse=float(
                np.sqrt(mean_squared_error(test_df[self.target], y_test_pred))
            ),
            test_mae=mean_absolute_error(test_df[self.target], y_test_pred),
        )

    def shap_values(self, df: pd.DataFrame) -> np.ndarray:
        self._check_fitted()
        return self._explainer.shap_values(df[self.features])

    @property
    def base_value(self) -> float:
        self._check_fitted()
        return float(self._explainer.expected_value)

    def global_importance(self, df: pd.DataFrame) -> pd.Series:
        """Mean absolute SHAP value per feature, sorted ascending."""
        sv = self.shap_values(df)
        return pd.Series(
            np.abs(sv).mean(axis=0), index=self.features
        ).sort_values(ascending=True)

    def _check_fitted(self) -> None:
        if not self._fitted:
            raise RuntimeError("Call .fit(train_df) before using this model.")
