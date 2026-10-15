#!/usr/bin/env python3
"""Refit PhysioRisk_2axis_v2 after the frozen creatinine unit repair.

This script preserves the historical cohort, split, DemoRisk values,
residualization, axis definitions, Cox specification, and penalization. It does
not construct or fit CalibratedTotalRisk and refuses to overwrite any output.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from lifelines import CoxPHFitter
from lifelines.utils import concordance_index
from patsy import build_design_matrices, dmatrix
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression


REPO = Path(__file__).resolve().parents[1]
PARENT_COMMIT = "40cfbdbe187789207d74bae9f803f319f63cb3de"
DEFAULT_HISTORICAL_DIR = Path("/home/ubuntu2204/longevity/data/physiorisk/data")

ID_COL = "SEQN"
TIME_COL = "PERMTH_INT"
EVENT_COL = "MORTSTAT"
AGE_COL = "RIDAGEYR"
SEX_COL = "RIAGENDR"
BASELINE_COL = "BaselineRisk"  # Historical filename/column; scientifically DemoRisk.
SPLIT_COL = "cycle_start_year"

BIOMARKER_COLS = [
    "LBXSAL",
    "LBXSCR",
    "LBXSAPSI",
    "LBXWBCSI",
    "LBXLYPCT",
    "LBXMCV",
    "LBXRDW",
]
BENCHMARK_BIOMARKERS = [
    "LBXSAL",
    "LBXSCR",
    "LBXGLU",
    "LBXLYPCT",
    "LBXMCV",
    "LBXRDW",
    "LBXSAPSI",
    "LBXWBCSI",
]
RESIDUAL_FORMULA = "cr(RIDAGEYR, df=4) + RIAGENDR"
AXIS_GROUPS = {
    "HematologicStress": [
        "LBXWBCSI_resid_z",
        "LBXLYPCT_resid_z",
        "LBXMCV_resid_z",
        "LBXRDW_resid_z",
    ],
    "RenalHepaticTurnover": [
        "LBXSCR_resid_z",
        "LBXSAL_resid_z",
        "LBXSAPSI_resid_z",
    ],
}
SIGN_FLIPS = {
    "LBXLYPCT_resid_z": -1.0,
    "LBXSAL_resid_z": -1.0,
}
PHYSIORISK_PENALIZER = 0.01

HISTORICAL_FILENAMES = {
    "development": "physiorisk_2axis_v1_train_scored_from_frozen_baseline_levinenocrp.parquet",
    "validation": "physiorisk_2axis_v1_test_scored_from_frozen_baseline_levinenocrp.parquet",
}
HISTORICAL_HASHES = {
    "development": "e8f435b5a8b68dbb477f04bad280252f563b9323e9bc9dea4eb7e945c22cbb86",
    "validation": "1455e24e8ca3e1f68eb58a779f7a4d48e46b8e54fa435ec00de5cf51256d08ca",
}
OUTPUT_FILENAMES = {
    "development_input": "physiorisk_2axis_v2_train_input_levinenocrp.parquet",
    "validation_input": "physiorisk_2axis_v2_test_input_levinenocrp.parquet",
    "development_axes": "physiorisk_2axis_v2_train_axes_levinenocrp.parquet",
    "validation_axes": "physiorisk_2axis_v2_test_axes_levinenocrp.parquet",
    "development_scored": "physiorisk_2axis_v2_train_scored_levinenocrp.parquet",
    "validation_scored": "physiorisk_2axis_v2_test_scored_levinenocrp.parquet",
    "coefficients": "physiorisk_2axis_v2_physio_cox_coefficients.csv",
    "validation_metrics": "physiorisk_2axis_v2_validation_metrics.csv",
    "reconciliation": "physiorisk_2axis_v2_reconciliation.json",
    "metadata": "physiorisk_2axis_v2_model_metadata.json",
    "manifest": "physiorisk_2axis_v2_artifact_manifest.json",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def id_sha256(frame: pd.DataFrame) -> str:
    values = "\n".join(str(value) for value in sorted(frame[ID_COL].astype(int))) + "\n"
    return hashlib.sha256(values.encode("utf-8")).hexdigest()


def require_file(path: Path) -> Path:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path


def assert_unique_ids(frame: pd.DataFrame, label: str) -> None:
    if frame[ID_COL].isna().any() or not frame[ID_COL].is_unique:
        raise AssertionError(f"{label} lacks unique, nonmissing SEQN")


def assert_same_ids(left: pd.DataFrame, right: pd.DataFrame, label: str) -> None:
    assert_unique_ids(left, f"{label} left")
    assert_unique_ids(right, f"{label} right")
    left_ids = set(left[ID_COL].astype(int))
    right_ids = set(right[ID_COL].astype(int))
    if left_ids != right_ids:
        raise AssertionError(
            f"{label} ID mismatch: left-only={len(left_ids-right_ids)}, "
            f"right-only={len(right_ids-left_ids)}"
        )


def assert_numeric_equal(
    left: pd.Series,
    right: pd.Series,
    label: str,
    *,
    atol: float = 0.0,
) -> float:
    left_values = pd.to_numeric(left, errors="coerce").to_numpy(dtype=float)
    right_values = pd.to_numeric(right, errors="coerce").to_numpy(dtype=float)
    if not np.allclose(left_values, right_values, rtol=0.0, atol=atol, equal_nan=True):
        finite = np.isfinite(left_values) & np.isfinite(right_values)
        max_difference = (
            float(np.max(np.abs(left_values[finite] - right_values[finite])))
            if finite.any()
            else float("nan")
        )
        raise AssertionError(f"{label} differs; max absolute difference={max_difference}")
    finite = np.isfinite(left_values) & np.isfinite(right_values)
    return (
        float(np.max(np.abs(left_values[finite] - right_values[finite])))
        if finite.any()
        else 0.0
    )


def safe_json(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): safe_json(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [safe_json(item) for item in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return None if not np.isfinite(value) else float(value)
    if isinstance(value, np.ndarray):
        return [safe_json(item) for item in value.tolist()]
    if isinstance(value, Path):
        return str(value)
    return value


def initialize_output_dir(output_dir: Path) -> Path:
    output_dir = output_dir.resolve()
    allowed_root = (REPO / "outputs").resolve()
    if allowed_root not in output_dir.parents:
        raise ValueError(f"output directory must be a child of {allowed_root}")
    if output_dir.exists():
        raise FileExistsError(f"refusing to overwrite existing output directory: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=False)
    return output_dir


def output_path(output_dir: Path, key: str) -> Path:
    path = output_dir / OUTPUT_FILENAMES[key]
    if path.exists():
        raise FileExistsError(f"refusing to overwrite output: {path}")
    if "v1" in path.name.lower() or "v2" not in path.name.lower():
        raise AssertionError(f"output is not safely v2-qualified: {path.name}")
    return path


def align_historical(corrected: pd.DataFrame, historical: pd.DataFrame) -> pd.DataFrame:
    assert_same_ids(corrected, historical, "corrected versus historical cohort")
    return corrected[[ID_COL]].merge(historical, on=ID_COL, how="left", validate="one_to_one")


def build_v2_input(corrected: pd.DataFrame, historical: pd.DataFrame) -> pd.DataFrame:
    historical_aligned = align_historical(corrected, historical)
    baseline = historical_aligned[[ID_COL, BASELINE_COL]]
    output = corrected.merge(baseline, on=ID_COL, how="left", validate="one_to_one")
    if output[BASELINE_COL].isna().any():
        raise AssertionError("DemoRisk join created missing values")
    expected = historical_aligned[BASELINE_COL]
    assert_numeric_equal(output[BASELINE_COL], expected, "frozen DemoRisk", atol=0.0)
    columns = [
        ID_COL,
        TIME_COL,
        EVENT_COL,
        AGE_COL,
        SEX_COL,
        SPLIT_COL,
        *BENCHMARK_BIOMARKERS,
        BASELINE_COL,
    ]
    return output[columns].copy()


def make_design_matrix(
    frame: pd.DataFrame,
    design_info=None,
) -> tuple[pd.DataFrame, Any]:
    base = frame[[AGE_COL, SEX_COL]].copy()
    if design_info is None:
        matrix = dmatrix(RESIDUAL_FORMULA, base, return_type="dataframe")
        return matrix, matrix.design_info
    matrix = build_design_matrices([design_info], base)[0]
    return (
        pd.DataFrame(matrix, index=base.index, columns=design_info.column_names),
        design_info,
    )


def fit_residualizers(development: pd.DataFrame) -> dict[str, Any]:
    matrix, design_info = make_design_matrix(development)
    models: dict[str, Any] = {}
    for biomarker in BIOMARKER_COLS:
        imputer = SimpleImputer(strategy="median")
        values = imputer.fit_transform(development[[biomarker]]).ravel()
        regression = LinearRegression()
        regression.fit(matrix, values)
        residuals = values - regression.predict(matrix)
        residual_mean = float(np.mean(residuals))
        residual_std = float(np.std(residuals, ddof=0))
        if residual_std == 0:
            residual_std = 1.0
        models[biomarker] = {
            "imputer": imputer,
            "regression": regression,
            "residual_mean": residual_mean,
            "residual_std": residual_std,
        }
    return {"design_info": design_info, "models": models}


def apply_residualizers(frame: pd.DataFrame, bundle: dict[str, Any]) -> pd.DataFrame:
    matrix, _ = make_design_matrix(frame, bundle["design_info"])
    output = pd.DataFrame(index=frame.index)
    for biomarker in BIOMARKER_COLS:
        model = bundle["models"][biomarker]
        values = model["imputer"].transform(frame[[biomarker]]).ravel()
        residuals = values - model["regression"].predict(matrix)
        output[f"{biomarker}_resid_z"] = (
            residuals - model["residual_mean"]
        ) / (model["residual_std"] + 1e-8)
    return output


def apply_signs(residuals: pd.DataFrame) -> pd.DataFrame:
    output = residuals.copy()
    for column, multiplier in SIGN_FLIPS.items():
        output[column] = output[column] * multiplier
    return output


def build_axes(residuals: pd.DataFrame) -> pd.DataFrame:
    output = pd.DataFrame(index=residuals.index)
    for axis, columns in AXIS_GROUPS.items():
        output[axis] = residuals[columns].mean(axis=1)
    return output


def residualizer_metadata(bundle: dict[str, Any]) -> dict[str, Any]:
    design_info = bundle["design_info"]
    spline_state = []
    for factor_info in design_info.factor_infos.values():
        transforms = factor_info.state.get("transforms", {}) if factor_info.state else {}
        for name, transform in transforms.items():
            spline_state.append(
                {
                    "name": name,
                    "class": transform.__class__.__name__,
                    "all_knots": safe_json(getattr(transform, "_all_knots", None)),
                    "constraints": safe_json(getattr(transform, "_constraints", None)),
                }
            )
    models = {}
    for biomarker, model in bundle["models"].items():
        models[biomarker] = {
            "imputation_strategy": "median",
            "imputation_statistic": float(model["imputer"].statistics_[0]),
            "linear_regression_intercept": float(model["regression"].intercept_),
            "linear_regression_coefficients": {
                column: float(coefficient)
                for column, coefficient in zip(
                    design_info.column_names, model["regression"].coef_
                )
            },
            "residual_mean": model["residual_mean"],
            "residual_sd_ddof0": model["residual_std"],
            "standardization_formula": "(residual - development residual mean) / (development residual SD + 1e-8)",
        }
    return {
        "formula": RESIDUAL_FORMULA,
        "design_columns": list(design_info.column_names),
        "spline_state": spline_state,
        "models": models,
    }


def score_physiorisk(
    model: CoxPHFitter,
    development_axes: pd.DataFrame,
    validation_axes: pd.DataFrame,
) -> tuple[pd.Series, pd.Series, dict[str, float]]:
    raw_development = pd.Series(
        np.log(model.predict_partial_hazard(development_axes).to_numpy().ravel()),
        index=development_axes.index,
    )
    raw_validation = pd.Series(
        np.log(model.predict_partial_hazard(validation_axes).to_numpy().ravel()),
        index=validation_axes.index,
    )
    mean = float(raw_development.mean())
    std = float(raw_development.std(ddof=1))
    if std == 0:
        raise AssertionError("development PhysioRisk raw score has zero SD")
    return (
        (raw_development - mean) / std,
        (raw_validation - mean) / std,
        {
            "development_raw_score_mean": mean,
            "development_raw_score_sd_ddof1": std,
            "formula": "(raw log partial hazard - development mean) / development sample SD",
        },
    )


def validation_metrics(frame: pd.DataFrame, score: str) -> dict[str, Any]:
    sample = frame[[TIME_COL, EVENT_COL, AGE_COL, score]].dropna().copy()
    sd = float(sample[score].std(ddof=1))
    standardized = f"{score}_validation_z"
    sample[standardized] = (sample[score] - sample[score].mean()) / sd
    model = CoxPHFitter()
    model.fit(
        sample[[TIME_COL, EVENT_COL, standardized]],
        duration_col=TIME_COL,
        event_col=EVENT_COL,
    )
    summary = model.summary.loc[standardized]
    return {
        "score": score,
        "validation_n": len(sample),
        "validation_events": int(sample[EVENT_COL].sum()),
        "validation_mean": float(sample[score].mean()),
        "validation_sd_ddof1": sd,
        "HR_per_validation_SD": float(summary["exp(coef)"]),
        "HR_95CI_low": float(summary["exp(coef) lower 95%"]),
        "HR_95CI_high": float(summary["exp(coef) upper 95%"]),
        "p": float(summary["p"]),
        "Harrell_C_index": float(
            concordance_index(sample[TIME_COL], -sample[score], sample[EVENT_COL])
        ),
        "pearson_corr_age": float(sample[score].corr(sample[AGE_COL], method="pearson")),
    }


def paired_comparison(old: pd.Series, corrected: pd.Series) -> dict[str, float]:
    old = old.reset_index(drop=True)
    corrected = corrected.reset_index(drop=True)
    difference = corrected - old
    old_decile = pd.qcut(old, 10, labels=False, duplicates="drop")
    corrected_decile = pd.qcut(corrected, 10, labels=False, duplicates="drop")
    return {
        "pearson": float(old.corr(corrected, method="pearson")),
        "spearman": float(old.corr(corrected, method="spearman")),
        "mean_absolute_difference": float(difference.abs().mean()),
        "sd_of_difference_ddof1": float(difference.std(ddof=1)),
        "changed_decile_n": int((old_decile != corrected_decile).sum()),
        "changed_decile_percent": float(100.0 * (old_decile != corrected_decile).mean()),
        "max_absolute_difference": float(difference.abs().max()),
    }


def target_result(observed: float, expected: float, tolerance: float) -> dict[str, Any]:
    difference = abs(observed - expected)
    return {
        "observed": observed,
        "expected_approximately": expected,
        "absolute_difference": difference,
        "absolute_tolerance": tolerance,
        "reconciles": difference <= tolerance,
    }


def write_parquet(frame: pd.DataFrame, path: Path) -> None:
    if path.exists():
        raise FileExistsError(path)
    frame.to_parquet(path, index=False)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--corrected-staging-dir", type=Path, required=True)
    parser.add_argument("--historical-dir", type=Path, default=DEFAULT_HISTORICAL_DIR)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    head = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=REPO, text=True
    ).strip()
    if head != PARENT_COMMIT:
        raise AssertionError(f"HEAD {head} does not equal frozen parent {PARENT_COMMIT}")

    corrected_outputs = args.corrected_staging_dir.resolve() / "outputs"
    historical_dir = args.historical_dir.resolve()
    corrected_paths = {
        "development": require_file(corrected_outputs / "development_cohort.parquet"),
        "validation": require_file(corrected_outputs / "validation_cohort.parquet"),
    }
    historical_paths = {
        cohort: require_file(historical_dir / filename)
        for cohort, filename in HISTORICAL_FILENAMES.items()
    }
    for cohort, path in historical_paths.items():
        actual_hash = sha256_file(path)
        if actual_hash != HISTORICAL_HASHES[cohort]:
            raise AssertionError(f"historical {cohort} hash mismatch: {actual_hash}")

    corrected = {key: pd.read_parquet(path) for key, path in corrected_paths.items()}
    historical = {key: pd.read_parquet(path) for key, path in historical_paths.items()}
    expected_counts = {
        "development": (13090, 2520),
        "validation": (6739, 416),
    }
    for cohort in ["development", "validation"]:
        count, deaths = expected_counts[cohort]
        if len(corrected[cohort]) != count or int(corrected[cohort][EVENT_COL].sum()) != deaths:
            raise AssertionError(f"corrected {cohort} count/event invariant failed")
        assert_same_ids(corrected[cohort], historical[cohort], cohort)

    inputs = {
        cohort: build_v2_input(corrected[cohort], historical[cohort])
        for cohort in ["development", "validation"]
    }
    old_aligned = {
        cohort: align_historical(corrected[cohort], historical[cohort])
        for cohort in ["development", "validation"]
    }

    new_bundle = fit_residualizers(inputs["development"])
    old_bundle = fit_residualizers(old_aligned["development"])
    new_residuals = {
        cohort: apply_signs(apply_residualizers(inputs[cohort], new_bundle))
        for cohort in ["development", "validation"]
    }
    old_residuals = {
        cohort: apply_signs(apply_residualizers(old_aligned[cohort], old_bundle))
        for cohort in ["development", "validation"]
    }
    hematologic_residual_max_differences = {}
    for cohort in ["development", "validation"]:
        for column in AXIS_GROUPS["HematologicStress"]:
            key = f"{cohort}:{column}"
            hematologic_residual_max_differences[key] = assert_numeric_equal(
                new_residuals[cohort][column],
                old_residuals[cohort][column],
                f"unchanged {key}",
                atol=1e-12,
            )

    new_axes = {cohort: build_axes(new_residuals[cohort]) for cohort in new_residuals}
    old_axes = {cohort: build_axes(old_residuals[cohort]) for cohort in old_residuals}
    hematologic_axis_max_differences = {}
    for cohort in ["development", "validation"]:
        hematologic_axis_max_differences[cohort] = assert_numeric_equal(
            new_axes[cohort]["HematologicStress"],
            old_aligned[cohort]["HematologicStress"],
            f"{cohort} HematologicStress versus historical v1",
            atol=1e-12,
        )
        assert_numeric_equal(
            old_axes[cohort]["RenalHepaticTurnover"],
            old_aligned[cohort]["RenalHepaticTurnover"],
            f"reconstructed historical {cohort} RenalHepaticTurnover",
            atol=1e-12,
        )

    fit_frame = new_axes["development"].copy()
    fit_frame[TIME_COL] = inputs["development"][TIME_COL].to_numpy()
    fit_frame[EVENT_COL] = inputs["development"][EVENT_COL].to_numpy()
    physio_model = CoxPHFitter(penalizer=PHYSIORISK_PENALIZER)
    physio_model.fit(fit_frame, duration_col=TIME_COL, event_col=EVENT_COL)
    development_score, validation_score, score_standardization = score_physiorisk(
        physio_model, new_axes["development"], new_axes["validation"]
    )

    scored = {}
    axis_exports = {}
    for cohort, score in [
        ("development", development_score),
        ("validation", validation_score),
    ]:
        axis_exports[cohort] = pd.concat(
            [
                inputs[cohort][[ID_COL]].reset_index(drop=True),
                new_residuals[cohort].reset_index(drop=True),
                new_axes[cohort].reset_index(drop=True),
            ],
            axis=1,
        )
        scored[cohort] = inputs[cohort].copy()
        for axis in AXIS_GROUPS:
            scored[cohort][axis] = new_axes[cohort][axis].to_numpy()
        scored[cohort]["PhysioRisk_2axis_v2"] = score.to_numpy()
        if any("TotalRisk" in column for column in scored[cohort].columns):
            raise AssertionError("CalibratedTotalRisk field unexpectedly present")

    validation_rows = [
        validation_metrics(scored["validation"], "HematologicStress"),
        validation_metrics(scored["validation"], "RenalHepaticTurnover"),
        validation_metrics(scored["validation"], "PhysioRisk_2axis_v2"),
    ]
    validation_table = pd.DataFrame(validation_rows)

    old_rht_comparison = {
        cohort: paired_comparison(
            old_aligned[cohort]["RenalHepaticTurnover"],
            scored[cohort]["RenalHepaticTurnover"],
        )
        for cohort in ["development", "validation"]
    }
    old_physio_comparison = {
        cohort: paired_comparison(
            old_aligned[cohort]["PhysioRisk_2axis"],
            scored[cohort]["PhysioRisk_2axis_v2"],
        )
        for cohort in ["development", "validation"]
    }
    affected = inputs["development"][SPLIT_COL].eq(2001)
    affected_cycle_means = {
        "historical_v1": float(
            old_aligned["development"].loc[affected, "RenalHepaticTurnover"].mean()
        ),
        "corrected_v2": float(
            scored["development"].loc[affected, "RenalHepaticTurnover"].mean()
        ),
    }

    coefficients = []
    raw_score_sd = score_standardization["development_raw_score_sd_ddof1"]
    for axis in AXIS_GROUPS:
        summary = physio_model.summary.loc[axis]
        raw_coefficient = float(physio_model.params_.loc[axis])
        axis_sd = float(new_axes["development"][axis].std(ddof=1))
        coefficients.append(
            {
                "axis": axis,
                "raw_coefficient": raw_coefficient,
                "exp_raw_coefficient": float(np.exp(raw_coefficient)),
                "se_raw_coefficient": float(summary["se(coef)"]),
                "p": float(summary["p"]),
                "development_axis_mean": float(new_axes["development"][axis].mean()),
                "development_axis_sd_ddof1": axis_sd,
                "coefficient_per_development_axis_sd": raw_coefficient * axis_sd,
                "final_standardized_score_weight": raw_coefficient / raw_score_sd,
            }
        )
    coefficients_table = pd.DataFrame(coefficients)
    standardized_weights = dict(
        zip(
            coefficients_table["axis"],
            coefficients_table["final_standardized_score_weight"],
        )
    )

    new_creatinine_model = new_bundle["models"]["LBXSCR"]
    creatinine_residual_diagnostics = {
        "development_residual_mean": float(
            new_residuals["development"]["LBXSCR_resid_z"].mean()
        ),
        "development_residual_sd_ddof0": float(
            new_residuals["development"]["LBXSCR_resid_z"].std(ddof=0)
        ),
        "validation_residual_mean": float(
            new_residuals["validation"]["LBXSCR_resid_z"].mean()
        ),
        "validation_residual_sd_ddof0": float(
            new_residuals["validation"]["LBXSCR_resid_z"].std(ddof=0)
        ),
        "unstandardized_development_residual_sd_ddof0": new_creatinine_model[
            "residual_std"
        ],
    }

    metrics_by_score = {row["score"]: row for row in validation_rows}
    raw_coefficients = dict(zip(coefficients_table["axis"], coefficients_table["raw_coefficient"]))
    target_checks = {
        "development_rht_pearson": target_result(
            old_rht_comparison["development"]["pearson"], 0.7714, 0.0005
        ),
        "development_rht_spearman": target_result(
            old_rht_comparison["development"]["spearman"], 0.7899, 0.0005
        ),
        "development_rht_mad": target_result(
            old_rht_comparison["development"]["mean_absolute_difference"], 0.2476, 0.0005
        ),
        "development_rht_sd_difference": target_result(
            old_rht_comparison["development"]["sd_of_difference_ddof1"], 0.4065, 0.0005
        ),
        "development_rht_changed_decile_percent": target_result(
            old_rht_comparison["development"]["changed_decile_percent"], 68.39, 0.02
        ),
        "validation_rht_pearson": target_result(
            old_rht_comparison["validation"]["pearson"], 0.8039, 0.0005
        ),
        "validation_rht_spearman": target_result(
            old_rht_comparison["validation"]["spearman"], 0.9156, 0.0005
        ),
        "validation_rht_mad": target_result(
            old_rht_comparison["validation"]["mean_absolute_difference"], 0.1808, 0.0005
        ),
        "validation_rht_sd_difference": target_result(
            old_rht_comparison["validation"]["sd_of_difference_ddof1"], 0.3597, 0.0005
        ),
        "validation_rht_changed_decile_percent": target_result(
            old_rht_comparison["validation"]["changed_decile_percent"], 57.32, 0.02
        ),
        "affected_cycle_old_rht_mean": target_result(
            affected_cycle_means["historical_v1"], 0.6519, 0.0005
        ),
        "affected_cycle_corrected_rht_mean": target_result(
            affected_cycle_means["corrected_v2"], 0.0328, 0.0005
        ),
        "hematologic_standardized_weight": target_result(
            standardized_weights["HematologicStress"], 1.499210, 0.000005
        ),
        "rht_standardized_weight": target_result(
            standardized_weights["RenalHepaticTurnover"], 0.857262, 0.000005
        ),
        "hematologic_validation_hr": target_result(
            metrics_by_score["HematologicStress"]["HR_per_validation_SD"], 1.3053, 0.0005
        ),
        "hematologic_validation_cindex": target_result(
            metrics_by_score["HematologicStress"]["Harrell_C_index"], 0.6360, 0.0005
        ),
        "rht_validation_hr": target_result(
            metrics_by_score["RenalHepaticTurnover"]["HR_per_validation_SD"], 1.1921, 0.0005
        ),
        "rht_validation_ci_low": target_result(
            metrics_by_score["RenalHepaticTurnover"]["HR_95CI_low"], 1.1581, 0.0005
        ),
        "rht_validation_ci_high": target_result(
            metrics_by_score["RenalHepaticTurnover"]["HR_95CI_high"], 1.2271, 0.0005
        ),
        "rht_validation_cindex": target_result(
            metrics_by_score["RenalHepaticTurnover"]["Harrell_C_index"], 0.6176, 0.0005
        ),
        "physiorisk_validation_hr": target_result(
            metrics_by_score["PhysioRisk_2axis_v2"]["HR_per_validation_SD"], 1.3849, 0.0005
        ),
        "physiorisk_validation_cindex": target_result(
            metrics_by_score["PhysioRisk_2axis_v2"]["Harrell_C_index"], 0.6632, 0.0005
        ),
        "development_physiorisk_pearson": target_result(
            old_physio_comparison["development"]["pearson"], 0.9406, 0.0005
        ),
        "development_physiorisk_spearman": target_result(
            old_physio_comparison["development"]["spearman"], 0.9443, 0.0005
        ),
        "validation_physiorisk_pearson": target_result(
            old_physio_comparison["validation"]["pearson"], 0.9528, 0.0005
        ),
        "validation_physiorisk_spearman": target_result(
            old_physio_comparison["validation"]["spearman"], 0.9826, 0.0005
        ),
    }
    rht_p = metrics_by_score["RenalHepaticTurnover"]["p"]
    target_checks["rht_validation_p_log10"] = target_result(
        float(np.log10(rht_p)), float(np.log10(1.26e-32)), 0.02
    )
    if not all(check["reconciles"] for check in target_checks.values()):
        failed = [name for name, check in target_checks.items() if not check["reconciles"]]
        failed_details = {name: target_checks[name] for name in failed}
        raise AssertionError(
            f"independent audit targets failed: {json.dumps(failed_details, sort_keys=True)}; "
            f"coefficient table={coefficients_table.to_dict(orient='records')}"
        )

    reconciliation = {
        "status": "pass",
        "cohort_identity": {
            cohort: {
                "n": len(inputs[cohort]),
                "deaths": int(inputs[cohort][EVENT_COL].sum()),
                "id_sha256": id_sha256(inputs[cohort]),
                "identical_to_historical_v1": True,
                "DemoRisk_exactly_identical_to_historical_v1": True,
            }
            for cohort in ["development", "validation"]
        },
        "hematologic_constituent_residual_max_abs_differences": hematologic_residual_max_differences,
        "hematologic_axis_max_abs_differences": hematologic_axis_max_differences,
        "creatinine_residual_diagnostics": creatinine_residual_diagnostics,
        "RenalHepaticTurnover_old_vs_corrected": old_rht_comparison,
        "affected_2001_2002_development_RenalHepaticTurnover_mean": affected_cycle_means,
        "PhysioRisk_old_vs_corrected": old_physio_comparison,
        "validation_metrics": validation_rows,
        "target_checks": target_checks,
        "all_independent_targets_reconcile": True,
        "CalibratedTotalRisk_refit": False,
    }

    metadata = {
        "model_name": "PhysioRisk_2axis_v2",
        "parent_commit": PARENT_COMMIT,
        "current_head": head,
        "terminology": {
            "scientific_name": "DemoRisk",
            "historical_column_name": BASELINE_COL,
        },
        "input_artifacts": {
            "corrected_development_cohort": {
                "path": str(corrected_paths["development"]),
                "sha256": sha256_file(corrected_paths["development"]),
            },
            "corrected_validation_cohort": {
                "path": str(corrected_paths["validation"]),
                "sha256": sha256_file(corrected_paths["validation"]),
            },
            "historical_development_DemoRisk_carrier": {
                "path": str(historical_paths["development"]),
                "sha256": sha256_file(historical_paths["development"]),
            },
            "historical_validation_DemoRisk_carrier": {
                "path": str(historical_paths["validation"]),
                "sha256": sha256_file(historical_paths["validation"]),
            },
        },
        "cohorts": reconciliation["cohort_identity"],
        "residualization": residualizer_metadata(new_bundle),
        "axis_definitions": AXIS_GROUPS,
        "sign_flips": SIGN_FLIPS,
        "axis_aggregation": "arithmetic mean of listed signed standardized residuals",
        "physiology_cox": {
            "duration": TIME_COL,
            "event": EVENT_COL,
            "development_only_fit": True,
            "penalizer": PHYSIORISK_PENALIZER,
            "l1_ratio": 0.0,
            "raw_coefficients": raw_coefficients,
        },
        "PhysioRisk_standardization": score_standardization,
        "final_standardized_score_weights": {
            row["axis"]: row["final_standardized_score_weight"]
            for row in coefficients
        },
        "CalibratedTotalRisk_refit": False,
        "PhenoAge_NCP_recomputed": False,
    }

    output_dir = initialize_output_dir(args.output_dir)
    paths = {key: output_path(output_dir, key) for key in OUTPUT_FILENAMES}
    write_parquet(inputs["development"], paths["development_input"])
    write_parquet(inputs["validation"], paths["validation_input"])
    write_parquet(axis_exports["development"], paths["development_axes"])
    write_parquet(axis_exports["validation"], paths["validation_axes"])
    write_parquet(scored["development"], paths["development_scored"])
    write_parquet(scored["validation"], paths["validation_scored"])
    coefficients_table.to_csv(paths["coefficients"], index=False)
    validation_table.to_csv(paths["validation_metrics"], index=False)
    paths["reconciliation"].write_text(
        json.dumps(safe_json(reconciliation), indent=2, sort_keys=True) + "\n"
    )
    paths["metadata"].write_text(
        json.dumps(safe_json(metadata), indent=2, sort_keys=True) + "\n"
    )

    manifest_records = []
    for key, path in paths.items():
        if key == "manifest":
            continue
        record = {
            "artifact": key,
            "path": str(path),
            "sha256": sha256_file(path),
            "bytes": path.stat().st_size,
        }
        if path.suffix == ".parquet":
            record["rows"] = len(pd.read_parquet(path))
        elif path.suffix == ".csv":
            record["rows"] = len(pd.read_csv(path))
        manifest_records.append(record)
    paths["manifest"].write_text(
        json.dumps(manifest_records, indent=2, sort_keys=True) + "\n"
    )

    print(
        json.dumps(
            safe_json(
                {
                    "status": "pass",
                    "output_dir": output_dir,
                    "coefficients": coefficients,
                    "PhysioRisk_standardization": score_standardization,
                    "validation_metrics": validation_rows,
                    "reconciliation": reconciliation,
                    "artifact_manifest": manifest_records,
                }
            ),
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
