"""
Command-line entrypoint for the NPA EWS pipeline.

Usage
-----
    npa-ews run              # full pipeline: FE regression + XGBoost + stress test
    npa-ews run --stage fe   # just the fixed-effects regression
    npa-ews run --stage xgb  # just the XGBoost + SHAP stage
    npa-ews run --stage stress
    npa-ews --version

This replaces the original "cd notebooks && python 03_panel_regression.py
&& python 04_xgboost_shap.py && python 05_stress_test.py" instructions
with a single, testable, loggable command.
"""
from __future__ import annotations

import argparse
import logging
import sys

from npa_ews import __version__, config, data, stress
from npa_ews.models import FixedEffectsRegressor, GnpaXGBModel

logger = logging.getLogger("npa_ews")


def _setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )


def run_fe_stage(ml_df) -> FixedEffectsRegressor:
    logger.info("Fitting fixed-effects panel regression...")
    fe = FixedEffectsRegressor()
    result = fe.fit(ml_df)
    logger.info(
        "FE regression: R^2=%.3f, n=%d, coefficients=%s",
        result.r_squared,
        result.n_obs,
        {k: round(v, 4) for k, v in result.coefficients.items()},
    )
    return fe


def run_xgb_stage(ml_df) -> GnpaXGBModel:
    train = ml_df[ml_df["year"] <= config.TRAIN_YEAR_MAX]
    test = ml_df[ml_df["year"] >= config.TEST_YEAR_MIN]
    logger.info(
        "XGBoost train/test split: train=%d obs (<=%d), test=%d obs (>=%d)",
        len(train), config.TRAIN_YEAR_MAX, len(test), config.TEST_YEAR_MIN,
    )
    model = GnpaXGBModel().fit(train, test)
    metrics = model.evaluate(train, test)
    logger.info(
        "XGBoost: train_R^2=%.3f test_R^2=%.3f test_RMSE=%.3f test_MAE=%.3f",
        metrics.train_r2, metrics.test_r2, metrics.test_rmse, metrics.test_mae,
    )
    return model


def run_stress_stage(fe: FixedEffectsRegressor, panel) -> None:
    baseline = panel[panel["year"] == 2024].dropna(
        subset=config.FEATURES
    ).set_index("bank_group")
    stress_df = stress.run_stress_test(fe.result, baseline)
    logger.info("Stress test results:\n%s", stress_df.round(2).to_string())

    breaches = stress.find_pca_breaches(stress_df)
    if breaches:
        logger.warning("PCA Threshold 1 (%.1f%%) breaches: %s", stress.PCA_THRESHOLD_1, breaches)
    else:
        logger.info("No PCA Threshold 1 breaches under any scenario.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="npa-ews", description=__doc__)
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command", required=True)

    run_p = sub.add_parser("run", help="Run the pipeline")
    run_p.add_argument(
        "--stage",
        choices=["all", "fe", "xgb", "stress"],
        default="all",
    )
    run_p.add_argument("-v", "--verbose", action="store_true")

    args = parser.parse_args(argv)
    _setup_logging(getattr(args, "verbose", False))

    if args.command == "run":
        panel = data.load_banking_panel()
        ml_df = data.get_model_ready_frame(panel)

        fe = None
        if args.stage in ("all", "fe", "stress"):
            fe = run_fe_stage(ml_df)
        if args.stage in ("all", "xgb"):
            run_xgb_stage(ml_df)
        if args.stage in ("all", "stress"):
            assert fe is not None
            run_stress_stage(fe, panel)

    return 0


if __name__ == "__main__":
    sys.exit(main())
