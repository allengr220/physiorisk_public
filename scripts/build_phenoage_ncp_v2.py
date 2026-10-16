#!/usr/bin/env python3
"""Build the published-form PhenoAge no-CRP v2 comparator.

The builder reads frozen PhysioRisk v2 participant inputs and frozen historical
v1 artifacts, validates cohort identity, reproduces the historical comparator,
and writes only new v2-qualified outputs. It does not construct or fit
CalibratedTotalRisk and refuses to overwrite an existing output directory.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import warnings
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
PARENT_COMMIT = "7abcbc11a3eda981b2f4d88e385cb0486f1ed6d7"
DEFAULT_V2_DIR = REPO / "outputs" / "physiorisk_2axis_v2_refit"
DEFAULT_HISTORICAL_DIR = Path("/home/ubuntu2204/longevity/data/physiorisk/data")

ID = "SEQN"
TIME = "PERMTH_INT"
EVENT = "MORTSTAT"
AGE = "RIDAGEYR"
SEX = "RIAGENDR"
CYCLE = "cycle_start_year"
RAW_V2 = "PhenoAge_NCP_v2"
ACCEL_V2 = "PhenoAge_NCP_acceleration_v2"

PHENO_COLS = [
    "LBXSAL",
    "LBXSCR",
    "LBXGLU",
    "LBXLYPCT",
    "LBXMCV",
    "LBXRDW",
    "LBXSAPSI",
    "LBXWBCSI",
]

INPUT_FILES = {
    "development_v2": "physiorisk_2axis_v2_train_scored_levinenocrp.parquet",
    "validation_v2": "physiorisk_2axis_v2_test_scored_levinenocrp.parquet",
    "development_historical": "physiorisk_2axis_v1_train_scored_from_frozen_baseline_levinenocrp.parquet",
    "validation_historical": "physiorisk_2axis_v1_test_scored_from_frozen_baseline_levinenocrp.parquet",
}

INPUT_HASHES = {
    "development_v2": "578b08930f8ea524e205a6d7754b2c07739ed775d081346b39e24fd27890cab1",
    "validation_v2": "e623e1e0d59da80e616a29a32821ab35552601864b650f239fde2566c362920d",
    "development_historical": "e8f435b5a8b68dbb477f04bad280252f563b9323e9bc9dea4eb7e945c22cbb86",
    "validation_historical": "1455e24e8ca3e1f68eb58a779f7a4d48e46b8e54fa435ec00de5cf51256d08ca",
}

OUTPUT_FILES = {
    "development_comparator": "phenoage_ncp_v2_development_comparator.parquet",
    "validation_comparator": "phenoage_ncp_v2_validation_comparator.parquet",
    "unit_contract_csv": "phenoage_ncp_v2_unit_contract.csv",
    "unit_contract_json": "phenoage_ncp_v2_unit_contract.json",
    "acceleration_metadata": "phenoage_ncp_v2_acceleration_model_metadata.json",
    "validation_metrics": "phenoage_ncp_v2_validation_metrics.csv",
    "reconciliation": "phenoage_ncp_v2_reconciliation.json",
    "paired_bootstrap": "phenoage_ncp_v2_paired_physiorisk_bootstrap.csv",
    "manifest": "phenoage_ncp_v2_artifact_manifest.json",
}

GLUCOSE_CONTRACT = [
    ("1999-2000", 1999, "LAB10AM.XPT", "LBXGLU", "mg/dL", 0.05551, "LBXGLU * 0.05551"),
    ("2001-2002", 2001, "L40_B.XPT", "LBDSGLSI", "mmol/L", 1.0, "LBDSGLSI"),
    ("2003-2004", 2003, "L40_C.XPT", "LBDSGLSI", "mmol/L", 1.0, "LBDSGLSI"),
    ("2005-2006", 2005, "GLU_D.XPT", "LBXGLU", "mg/dL", 0.05551, "LBXGLU * 0.05551"),
    ("2007-2008", 2007, "GLU_E.XPT", "LBXGLU", "mg/dL", 0.05551, "LBXGLU * 0.05551"),
    ("2009-2010", 2009, "GLU_F.XPT", "LBXGLU", "mg/dL", 0.05551, "LBXGLU * 0.05551"),
    ("2011-2012", 2011, "GLU_G.XPT", "LBXGLU", "mg/dL", 0.05551, "LBXGLU * 0.05551"),
    ("2013-2014", 2013, "GLU_H.XPT", "LBXGLU", "mg/dL", 0.05551, "LBXGLU * 0.05551"),
    ("2015-2016", 2015, "GLU_I.XPT", "LBXGLU", "mg/dL", 0.05551, "LBXGLU * 0.05551"),
]

PUBLISHED_INPUT_CONTRACT = {
    "albumin": {
        "canonical_column": "LBXSAL",
        "canonical_unit": "g/dL",
        "coefficient_unit": "g/L",
        "conversion": "LBXSAL * 10",
    },
    "creatinine": {
        "canonical_column": "LBXSCR",
        "canonical_unit": "mg/dL",
        "coefficient_unit": "umol/L",
        "conversion": "LBXSCR * 88.4",
    },
    "glucose": {
        "canonical_column": "LBXGLU",
        "canonical_unit": "cycle-specific; see glucose_cycle_contract",
        "coefficient_unit": "mmol/L",
        "conversion": "explicit cycle/source contract; linear term",
    },
    "lymphocyte_percentage": {
        "canonical_column": "LBXLYPCT",
        "canonical_unit": "%",
        "coefficient_unit": "%",
        "conversion": "none",
    },
    "mean_cell_volume": {
        "canonical_column": "LBXMCV",
        "canonical_unit": "fL",
        "coefficient_unit": "fL",
        "conversion": "none",
    },
    "red_cell_distribution_width": {
        "canonical_column": "LBXRDW",
        "canonical_unit": "%",
        "coefficient_unit": "%",
        "conversion": "none",
    },
    "alkaline_phosphatase": {
        "canonical_column": "LBXSAPSI",
        "canonical_unit": "U/L",
        "coefficient_unit": "U/L",
        "conversion": "none",
    },
    "white_blood_cell_count": {
        "canonical_column": "LBXWBCSI",
        "canonical_unit": "10^3/uL (numerically equal to 10^9/L)",
        "coefficient_unit": "10^3/uL",
        "conversion": "none",
    },
    "chronological_age": {
        "canonical_column": "RIDAGEYR",
        "canonical_unit": "years",
        "coefficient_unit": "years",
        "conversion": "none",
    },
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def id_sha256(frame: pd.DataFrame) -> str:
    values = "\n".join(str(value) for value in sorted(frame[ID].astype(int))) + "\n"
    return hashlib.sha256(values.encode()).hexdigest()


def safe_json(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): safe_json(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [safe_json(item) for item in value]
    if isinstance(value, np.ndarray):
        return [safe_json(item) for item in value.tolist()]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value) if np.isfinite(value) else None
    if isinstance(value, Path):
        return str(value)
    return value


def require_file(path: Path) -> Path:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path


def verify_hash(path: Path, expected: str, label: str) -> None:
    actual = sha256_file(path)
    if actual != expected:
        raise AssertionError(f"{label} SHA256 {actual} != {expected}")


def initialize_output_dir(path: Path) -> Path:
    path = path.resolve()
    allowed = (REPO / "outputs").resolve()
    if allowed not in path.parents:
        raise ValueError(f"output directory must be a child of {allowed}")
    if path.exists():
        raise FileExistsError(f"refusing to overwrite existing output directory: {path}")
    path.mkdir(parents=True, exist_ok=False)
    return path


def output_path(output_dir: Path, key: str) -> Path:
    path = output_dir / OUTPUT_FILES[key]
    if path.exists():
        raise FileExistsError(f"refusing to overwrite output: {path}")
    if "v2" not in path.name.lower():
        raise AssertionError(f"output lacks v2 qualifier: {path.name}")
    return path


def assert_same_ids(left: pd.DataFrame, right: pd.DataFrame, label: str) -> None:
    if not left[ID].is_unique or not right[ID].is_unique:
        raise AssertionError(f"{label}: nonunique participant identifiers")
    if set(left[ID].astype(int)) != set(right[ID].astype(int)):
        raise AssertionError(f"{label}: participant identifiers differ")


def align_to(reference: pd.DataFrame, other: pd.DataFrame) -> pd.DataFrame:
    assert_same_ids(reference, other, "cohort alignment")
    return reference[[ID]].merge(other, on=ID, how="left", validate="one_to_one")


def impute_inputs(
    development: pd.DataFrame, validation: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame, SimpleImputer, dict[str, int]]:
    missing = {
        f"development:{column}": int(development[column].isna().sum())
        for column in PHENO_COLS
    }
    missing.update(
        {
            f"validation:{column}": int(validation[column].isna().sum())
            for column in PHENO_COLS
        }
    )
    if any(missing.values()):
        raise AssertionError(f"retained benchmark unexpectedly requires imputation: {missing}")
    imputer = SimpleImputer(strategy="median")
    dev = development.copy()
    val = validation.copy()
    dev[PHENO_COLS] = imputer.fit_transform(dev[PHENO_COLS])
    val[PHENO_COLS] = imputer.transform(val[PHENO_COLS])
    return dev, val, imputer, missing


def historical_score(frame: pd.DataFrame) -> pd.Series:
    """Exact repository implementation retained only for reconciliation."""
    return (
        -19.907
        - 0.0336 * frame["LBXSAL"]
        + 0.0095 * frame["LBXSCR"]
        + 0.1953 * np.log(frame["LBXGLU"].clip(lower=1e-6))
        - 0.0120 * frame["LBXLYPCT"]
        + 0.0268 * frame["LBXMCV"]
        + 0.3306 * frame["LBXRDW"]
        + 0.0019 * frame["LBXSAPSI"]
        + 0.0554 * frame["LBXWBCSI"]
        + 0.0804 * frame[AGE]
    )


def glucose_mmol_l(frame: pd.DataFrame) -> pd.Series:
    result = pd.Series(np.nan, index=frame.index, dtype=float)
    for _, year, _, _, source_unit, factor, _ in GLUCOSE_CONTRACT:
        selected = frame[CYCLE].eq(year)
        if source_unit == "mg/dL":
            result.loc[selected] = frame.loc[selected, "LBXGLU"] * factor
        else:
            result.loc[selected] = frame.loc[selected, "LBXGLU"]
    if result.isna().any():
        unknown = sorted(frame.loc[result.isna(), CYCLE].unique())
        raise AssertionError(f"glucose unit contract lacks cycles: {unknown}")
    return result


def corrected_score(frame: pd.DataFrame) -> pd.Series:
    albumin_g_l = frame["LBXSAL"] * 10.0
    creatinine_umol_l = frame["LBXSCR"] * 88.4
    glucose = glucose_mmol_l(frame)
    return (
        -19.907
        - 0.0336 * albumin_g_l
        + 0.0095 * creatinine_umol_l
        + 0.1953 * glucose
        - 0.0120 * frame["LBXLYPCT"]
        + 0.0268 * frame["LBXMCV"]
        + 0.3306 * frame["LBXRDW"]
        + 0.00188 * frame["LBXSAPSI"]
        + 0.0554 * frame["LBXWBCSI"]
        + 0.0804 * frame[AGE]
    )


def fit_acceleration(
    development: pd.DataFrame,
    validation: pd.DataFrame,
    development_score: pd.Series,
    validation_score: pd.Series,
) -> tuple[pd.Series, pd.Series, dict[str, Any]]:
    formula = f"cr({AGE}, df=4) + C({SEX})"
    x_dev = dmatrix(formula, development, return_type="dataframe")
    design_info = x_dev.design_info
    x_val = build_design_matrices([design_info], validation, return_type="dataframe")[0]
    model = LinearRegression().fit(x_dev, development_score)
    dev_accel = pd.Series(
        development_score.to_numpy() - model.predict(x_dev), index=development.index
    )
    val_accel = pd.Series(
        validation_score.to_numpy() - model.predict(x_val), index=validation.index
    )
    spline_state = []
    for factor in design_info.factor_infos.values():
        transforms = factor.state.get("transforms", {}) if factor.state else {}
        for name, transform in transforms.items():
            spline_state.append(
                {
                    "name": name,
                    "class": transform.__class__.__name__,
                    "all_knots": safe_json(getattr(transform, "_all_knots", None)),
                    "constraints": safe_json(getattr(transform, "_constraints", None)),
                }
            )
    metadata = {
        "formula": formula,
        "fit_cohort": "development only",
        "validation_transform": "frozen development design and regression",
        "design_columns": list(design_info.column_names),
        "spline_state": spline_state,
        "linear_regression_intercept": float(model.intercept_),
        "linear_regression_coefficients": {
            column: float(coefficient)
            for column, coefficient in zip(design_info.column_names, model.coef_)
        },
    }
    return dev_accel, val_accel, metadata


def validation_metrics(frame: pd.DataFrame, score: pd.Series, label: str) -> dict[str, Any]:
    sample = frame[[TIME, EVENT, AGE]].copy()
    sample["score"] = score
    sample = sample.dropna()
    sd = float(sample["score"].std(ddof=1))
    sample["score_z"] = (sample["score"] - sample["score"].mean()) / sd
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = CoxPHFitter(penalizer=0.0)
        model.fit(
            sample[[TIME, EVENT, "score_z"]],
            duration_col=TIME,
            event_col=EVENT,
        )
    summary = model.summary.loc["score_z"]
    return {
        "score": label,
        "validation_n": len(sample),
        "validation_deaths": int(sample[EVENT].sum()),
        "validation_mean": float(sample["score"].mean()),
        "validation_sd_ddof1": sd,
        "HR_per_validation_SD": float(summary["exp(coef)"]),
        "HR_95CI_low": float(summary["exp(coef) lower 95%"]),
        "HR_95CI_high": float(summary["exp(coef) upper 95%"]),
        "p": float(summary["p"]),
        "Harrell_C_index": float(
            concordance_index(sample[TIME], -sample["score"], sample[EVENT])
        ),
        "pearson_corr_age": float(sample["score"].corr(sample[AGE])),
    }


def distribution(score: pd.Series) -> dict[str, Any]:
    quantiles = score.quantile([0.0, 0.25, 0.5, 0.75, 1.0])
    return {
        "n": int(score.notna().sum()),
        "mean": float(score.mean()),
        "sd_ddof1": float(score.std(ddof=1)),
        "min": float(quantiles.loc[0.0]),
        "q25": float(quantiles.loc[0.25]),
        "median": float(quantiles.loc[0.5]),
        "q75": float(quantiles.loc[0.75]),
        "max": float(quantiles.loc[1.0]),
    }


def paired_comparison(old: pd.Series, corrected: pd.Series) -> dict[str, float]:
    old = old.reset_index(drop=True)
    corrected = corrected.reset_index(drop=True)
    difference = corrected - old
    return {
        "pearson": float(old.corr(corrected, method="pearson")),
        "spearman": float(old.corr(corrected, method="spearman")),
        "mean_absolute_difference": float(difference.abs().mean()),
        "mean_difference_corrected_minus_historical": float(difference.mean()),
        "sd_difference_ddof1": float(difference.std(ddof=1)),
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


def paired_bootstrap(
    validation: pd.DataFrame,
    physiorisk: pd.Series,
    acceleration: pd.Series,
    *,
    replicates: int = 2000,
    seed: int = 20260821,
) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    times = validation[TIME].to_numpy(dtype=float)
    events = validation[EVENT].to_numpy(dtype=int)
    physio = physiorisk.to_numpy(dtype=float)
    accel = acceleration.to_numpy(dtype=float)
    n = len(validation)
    differences = np.empty(replicates, dtype=float)
    failure_count = 0
    eventless_redraw_count = 0
    completed = 0
    while completed < replicates:
        indices = rng.integers(0, n, n)
        if events[indices].sum() == 0:
            eventless_redraw_count += 1
            continue
        try:
            physio_c = concordance_index(times[indices], -physio[indices], events[indices])
            accel_c = concordance_index(times[indices], -accel[indices], events[indices])
        except Exception:
            failure_count += 1
            continue
        differences[completed] = physio_c - accel_c
        completed += 1
    physio_point = float(concordance_index(times, -physio, events))
    accel_point = float(concordance_index(times, -accel, events))
    return {
        "method": "participant-level paired nonparametric bootstrap",
        "replicates_requested": replicates,
        "replicates_completed": completed,
        "seed": seed,
        "PhysioRisk_2axis_v2_C_index": physio_point,
        "PhenoAge_NCP_acceleration_v2_C_index": accel_point,
        "delta_C_PhysioRisk_minus_acceleration": physio_point - accel_point,
        "percentile_95CI_low": float(np.quantile(differences, 0.025)),
        "percentile_95CI_high": float(np.quantile(differences, 0.975)),
        "bootstrap_failure_count": failure_count,
        "eventless_redraw_count": eventless_redraw_count,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--v2-dir", type=Path, default=DEFAULT_V2_DIR)
    parser.add_argument("--historical-dir", type=Path, default=DEFAULT_HISTORICAL_DIR)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    head = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=REPO, text=True
    ).strip()
    if head != PARENT_COMMIT:
        raise AssertionError(f"HEAD {head} != frozen parent {PARENT_COMMIT}")

    v2_dir = args.v2_dir.resolve()
    historical_dir = args.historical_dir.resolve()
    input_paths = {
        "development_v2": require_file(v2_dir / INPUT_FILES["development_v2"]),
        "validation_v2": require_file(v2_dir / INPUT_FILES["validation_v2"]),
        "development_historical": require_file(
            historical_dir / INPUT_FILES["development_historical"]
        ),
        "validation_historical": require_file(
            historical_dir / INPUT_FILES["validation_historical"]
        ),
    }
    for label, path in input_paths.items():
        verify_hash(path, INPUT_HASHES[label], label)

    v2 = {
        "development": pd.read_parquet(input_paths["development_v2"]),
        "validation": pd.read_parquet(input_paths["validation_v2"]),
    }
    historical = {
        "development": pd.read_parquet(input_paths["development_historical"]),
        "validation": pd.read_parquet(input_paths["validation_historical"]),
    }
    expected = {"development": (13090, 2520), "validation": (6739, 416)}
    for cohort, (n, deaths) in expected.items():
        if len(v2[cohort]) != n or int(v2[cohort][EVENT].sum()) != deaths:
            raise AssertionError(f"{cohort} count/death invariant failed")
        assert_same_ids(v2[cohort], historical[cohort], cohort)
        historical[cohort] = align_to(v2[cohort], historical[cohort])

    v2_dev, v2_val, v2_imputer, missing = impute_inputs(
        v2["development"], v2["validation"]
    )
    old_dev, old_val, _, old_missing = impute_inputs(
        historical["development"], historical["validation"]
    )
    if any(old_missing.values()):
        raise AssertionError("historical benchmark unexpectedly required imputation")

    old_raw = {
        "development": historical_score(old_dev),
        "validation": historical_score(old_val),
    }
    corrected_raw = {
        "development": corrected_score(v2_dev),
        "validation": corrected_score(v2_val),
    }
    old_accel_dev, old_accel_val, _ = fit_acceleration(
        old_dev, old_val, old_raw["development"], old_raw["validation"]
    )
    corrected_accel_dev, corrected_accel_val, accel_metadata = fit_acceleration(
        v2_dev,
        v2_val,
        corrected_raw["development"],
        corrected_raw["validation"],
    )
    old_accel = {"development": old_accel_dev, "validation": old_accel_val}
    corrected_accel = {
        "development": corrected_accel_dev,
        "validation": corrected_accel_val,
    }

    historical_metrics = {
        "raw": validation_metrics(old_val, old_raw["validation"], "historical_raw_NCP"),
        "acceleration": validation_metrics(
            old_val, old_accel["validation"], "historical_NCP_acceleration"
        ),
    }
    corrected_metrics = {
        "raw": validation_metrics(v2_val, corrected_raw["validation"], RAW_V2),
        "acceleration": validation_metrics(
            v2_val, corrected_accel["validation"], ACCEL_V2
        ),
    }
    comparisons = {
        score: {
            cohort: paired_comparison(
                old_raw[cohort] if score == "raw" else old_accel[cohort],
                corrected_raw[cohort] if score == "raw" else corrected_accel[cohort],
            )
            for cohort in ["development", "validation"]
        }
        for score in ["raw", "acceleration"]
    }
    distributions = {
        "historical": {
            "raw": {cohort: distribution(old_raw[cohort]) for cohort in old_raw},
            "acceleration": {
                cohort: distribution(old_accel[cohort]) for cohort in old_accel
            },
        },
        "corrected_v2": {
            "raw": {
                cohort: distribution(corrected_raw[cohort]) for cohort in corrected_raw
            },
            "acceleration": {
                cohort: distribution(corrected_accel[cohort])
                for cohort in corrected_accel
            },
        },
    }

    bootstrap = paired_bootstrap(
        v2_val,
        v2_val["PhysioRisk_2axis_v2"],
        corrected_accel["validation"],
    )

    checks = {
        "historical_raw_hr": target_result(
            historical_metrics["raw"]["HR_per_validation_SD"], 3.9761176968, 1e-9
        ),
        "historical_raw_c": target_result(
            historical_metrics["raw"]["Harrell_C_index"], 0.8411083058, 1e-9
        ),
        "historical_raw_age_corr": target_result(
            historical_metrics["raw"]["pearson_corr_age"], 0.9613694861, 1e-9
        ),
        "historical_accel_hr": target_result(
            historical_metrics["acceleration"]["HR_per_validation_SD"],
            1.4321475073,
            1e-9,
        ),
        "historical_accel_c": target_result(
            historical_metrics["acceleration"]["Harrell_C_index"],
            0.6378574839,
            1e-9,
        ),
        "historical_accel_age_corr": target_result(
            historical_metrics["acceleration"]["pearson_corr_age"],
            0.03329887535,
            1e-9,
        ),
        "corrected_raw_hr": target_result(
            corrected_metrics["raw"]["HR_per_validation_SD"],
            2.3095887816385274,
            1e-10,
        ),
        "corrected_raw_ci_low": target_result(
            corrected_metrics["raw"]["HR_95CI_low"], 2.2047150442291525, 1e-10
        ),
        "corrected_raw_ci_high": target_result(
            corrected_metrics["raw"]["HR_95CI_high"], 2.41945114595776, 1e-10
        ),
        "corrected_raw_c": target_result(
            corrected_metrics["raw"]["Harrell_C_index"], 0.8447479384566133, 1e-12
        ),
        "corrected_raw_age_corr": target_result(
            corrected_metrics["raw"]["pearson_corr_age"], 0.9231196422719159, 1e-12
        ),
        "corrected_accel_hr": target_result(
            corrected_metrics["acceleration"]["HR_per_validation_SD"],
            1.2980038708129953,
            1e-10,
        ),
        "corrected_accel_ci_low": target_result(
            corrected_metrics["acceleration"]["HR_95CI_low"],
            1.256471395923165,
            1e-10,
        ),
        "corrected_accel_ci_high": target_result(
            corrected_metrics["acceleration"]["HR_95CI_high"],
            1.3409091954756667,
            1e-10,
        ),
        "corrected_accel_c": target_result(
            corrected_metrics["acceleration"]["Harrell_C_index"],
            0.654344247267949,
            1e-12,
        ),
        "corrected_accel_age_corr": target_result(
            corrected_metrics["acceleration"]["pearson_corr_age"],
            0.05088606117164435,
            1e-12,
        ),
    }
    comparison_targets = {
        ("raw", "development", "pearson"): 0.96743314197,
        ("raw", "development", "spearman"): 0.97829568909,
        ("raw", "development", "mean_absolute_difference"): 0.46856882483,
        ("raw", "validation", "pearson"): 0.96742822859,
        ("raw", "validation", "spearman"): 0.98151032973,
        ("raw", "validation", "mean_absolute_difference"): 0.46126887906,
        ("acceleration", "development", "pearson"): 0.70091639428,
        ("acceleration", "development", "spearman"): 0.69196007157,
        ("acceleration", "development", "mean_absolute_difference"): 0.31124732125,
        ("acceleration", "validation", "pearson"): 0.76553127852,
        ("acceleration", "validation", "spearman"): 0.86347475611,
        ("acceleration", "validation", "mean_absolute_difference"): 0.25774615823,
    }
    for (score, cohort, measure), expected_value in comparison_targets.items():
        checks[f"{score}_{cohort}_{measure}"] = target_result(
            comparisons[score][cohort][measure], expected_value, 1e-9
        )
    if not all(check["reconciles"] for check in checks.values()):
        failed = {name: check for name, check in checks.items() if not check["reconciles"]}
        raise AssertionError(f"audit targets failed: {json.dumps(failed, sort_keys=True)}")

    cohort_identity = {
        cohort: {
            "n": len(v2[cohort]),
            "deaths": int(v2[cohort][EVENT].sum()),
            "id_sha256": id_sha256(v2[cohort]),
            "identical_to_historical_v1": True,
            "identical_to_PhysioRisk_2axis_v2": True,
        }
        for cohort in ["development", "validation"]
    }
    formula = (
        "-19.907 - 0.0336*albumin_g_L + 0.0095*creatinine_umol_L "
        "+ 0.1953*glucose_mmol_L - 0.0120*lymphocyte_pct "
        "+ 0.0268*MCV + 0.3306*RDW + 0.00188*alkaline_phosphatase "
        "+ 0.0554*WBC + 0.0804*age"
    )
    contract_rows = []
    for cycle, year, source_file, source_variable, source_unit, factor, conversion in GLUCOSE_CONTRACT:
        contract_rows.append(
            {
                "cycle": cycle,
                "cycle_start_year": year,
                "chemistry_source_file": source_file,
                "canonical_column": "LBXGLU",
                "selected_source_variable": source_variable,
                "source_unit": source_unit,
                "target_unit": "mmol/L",
                "conversion_factor": factor,
                "conversion_formula": conversion,
                "formula_transform": "linear; no logarithm",
            }
        )
    unit_contract = {
        "schema_version": 1,
        "model": "PhenoAge_NCP_v2",
        "CRP_included": False,
        "formula": formula,
        "published_input_contract": PUBLISHED_INPUT_CONTRACT,
        "glucose_cycle_contract": contract_rows,
    }
    accel_metadata.update(
        {
            "model": ACCEL_V2,
            "source_score": RAW_V2,
            "imputation": {
                "strategy": "development median",
                "values_required_imputation": missing,
                "statistics": {
                    column: float(value)
                    for column, value in zip(PHENO_COLS, v2_imputer.statistics_)
                },
            },
        }
    )
    reconciliation = {
        "status": "pass",
        "parent_commit": PARENT_COMMIT,
        "cohort_identity": cohort_identity,
        "historical_validation_metrics": historical_metrics,
        "corrected_validation_metrics": corrected_metrics,
        "historical_vs_corrected": comparisons,
        "distributions": distributions,
        "paired_PhysioRisk_vs_acceleration_bootstrap": bootstrap,
        "target_checks": checks,
        "all_independent_targets_reconcile": True,
        "CalibratedTotalRisk_refit": False,
        "historical_artifacts_overwritten": False,
    }

    development_export = pd.DataFrame(
        {
            ID: v2_dev[ID].to_numpy(),
            RAW_V2: corrected_raw["development"].to_numpy(),
            ACCEL_V2: corrected_accel["development"].to_numpy(),
        }
    )
    validation_export = pd.DataFrame(
        {
            ID: v2_val[ID].to_numpy(),
            RAW_V2: corrected_raw["validation"].to_numpy(),
            ACCEL_V2: corrected_accel["validation"].to_numpy(),
        }
    )
    metrics_table = pd.DataFrame(
        [historical_metrics["raw"], historical_metrics["acceleration"], corrected_metrics["raw"], corrected_metrics["acceleration"]]
    )
    bootstrap_table = pd.DataFrame([bootstrap])

    output_dir = initialize_output_dir(args.output_dir)
    paths = {key: output_path(output_dir, key) for key in OUTPUT_FILES}
    development_export.to_parquet(paths["development_comparator"], index=False)
    validation_export.to_parquet(paths["validation_comparator"], index=False)
    pd.DataFrame(contract_rows).to_csv(paths["unit_contract_csv"], index=False)
    paths["unit_contract_json"].write_text(json.dumps(unit_contract, indent=2) + "\n")
    paths["acceleration_metadata"].write_text(
        json.dumps(safe_json(accel_metadata), indent=2, sort_keys=True) + "\n"
    )
    metrics_table.to_csv(paths["validation_metrics"], index=False)
    paths["reconciliation"].write_text(
        json.dumps(safe_json(reconciliation), indent=2, sort_keys=True) + "\n"
    )
    bootstrap_table.to_csv(paths["paired_bootstrap"], index=False)

    manifest = []
    for key, path in paths.items():
        if key == "manifest":
            continue
        record = {
            "artifact": key,
            "path": str(path),
            "sha256": sha256_file(path),
            "bytes": path.stat().st_size,
            "participant_level": path.suffix == ".parquet",
        }
        if path.suffix == ".parquet":
            record["rows"] = len(pd.read_parquet(path))
        manifest.append(record)
    paths["manifest"].write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")

    result = {
        "status": "pass",
        "output_dir": str(output_dir),
        "input_artifacts": {
            label: {"path": str(path), "sha256": sha256_file(path)}
            for label, path in input_paths.items()
        },
        "cohorts": cohort_identity,
        "corrected_validation_metrics": corrected_metrics,
        "historical_vs_corrected": comparisons,
        "paired_bootstrap": bootstrap,
        "all_independent_targets_reconcile": True,
        "output_artifacts": manifest
        + [
            {
                "artifact": "manifest",
                "path": str(paths["manifest"]),
                "sha256": sha256_file(paths["manifest"]),
                "bytes": paths["manifest"].stat().st_size,
                "participant_level": False,
            }
        ],
    }
    print(json.dumps(safe_json(result), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
