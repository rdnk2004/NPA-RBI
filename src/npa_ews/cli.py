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

from npa_ews import __version__, config, data, stress, validation
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


def run_validation_stage(ml_df) -> None:
    logger.info("Running walk-forward cross-validation...")
    result = validation.walk_forward_cv(ml_df)
    logger.info("Walk-forward CV folds:\n%s", result.summary_table().to_string(index=False))
    logger.info(
        "CV summary: MAE=%.3f +/- %.3f, RMSE=%.3f +/- %.3f (n_folds=%d)",
        result.mean_mae, result.std_mae, result.mean_rmse, result.std_rmse, len(result.folds),
    )

    logger.info("Comparing against naive/mean/OLS baselines (same folds)...")
    comparison = validation.compare_baselines(ml_df)
    logger.info("Baseline comparison (walk-forward MAE/RMSE, mean +/- std):\n%s", comparison.to_string())


def run_stress_stage(fe: FixedEffectsRegressor, ml_df, panel, *, n_boot: int = 300) -> None:
    baseline = panel[panel["year"] == 2024].dropna(
        subset=config.FEATURES
    ).set_index("bank_group")
    reliability = data.group_reliability(ml_df)
    logger.info("Bank group data reliability:\n%s", reliability.to_string())

    stress_df = stress.run_stress_test(fe.result, baseline)
    stress_df_annotated = data.annotate_reliability(stress_df, reliability)
    logger.info("Stress test point estimates:\n%s", stress_df_annotated.round(2).to_string())

    breaches = stress.find_pca_breaches(stress_df)
    if breaches:
        logger.warning("PCA Threshold 1 (%.1f%%) breaches: %s", stress.PCA_THRESHOLD_1, breaches)
    else:
        logger.info("No PCA Threshold 1 breaches under any scenario (point estimate).")

    logger.info("Running bootstrap uncertainty quantification (n_boot=%d)...", n_boot)
    boot_results = stress.bootstrap_stress_test(ml_df, baseline, n_boot=n_boot)
    for scenario_name, scenario_df in boot_results.items():
        annotated = data.annotate_reliability(scenario_df, reliability)
        logger.info("Bootstrap CI -- %s:\n%s", scenario_name, annotated.to_string())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="npa-ews", description=__doc__)
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command", required=True)

    run_p = sub.add_parser("run", help="Run the pipeline")
    run_p.add_argument(
        "--stage",
        choices=["all", "fe", "xgb", "stress", "validate"],
        default="all",
    )
    run_p.add_argument("-v", "--verbose", action="store_true")
    run_p.add_argument(
        "--n-boot", type=int, default=300,
        help="Bootstrap resamples for stress-test CIs (default: 300; use 1000+ for report-quality figures).",
    )

    serve_p = sub.add_parser("serve", help="Run the FastAPI server")
    serve_p.add_argument("--host", default="127.0.0.1")
    serve_p.add_argument("--port", type=int, default=8000)
    serve_p.add_argument("--reload", action="store_true")

    args = parser.parse_args(argv)
    _setup_logging(getattr(args, "verbose", False))

    if args.command == "serve":
        import uvicorn

        logger.info("Starting API server at http://%s:%d (docs at /docs)", args.host, args.port)
        uvicorn.run("npa_ews.api:app", host=args.host, port=args.port, reload=args.reload)
        return 0

    if args.command == "run":
        panel = data.load_banking_panel()
        ml_df = data.get_model_ready_frame(panel)

        fe = None
        if args.stage in ("all", "fe", "stress"):
            fe = run_fe_stage(ml_df)
        if args.stage in ("all", "xgb"):
            run_xgb_stage(ml_df)
        if args.stage in ("all", "validate"):
            run_validation_stage(ml_df)
        if args.stage in ("all", "stress"):
            assert fe is not None
            run_stress_stage(fe, ml_df, panel, n_boot=args.n_boot)

    return 0


if __name__ == "__main__":
    sys.exit(main())
