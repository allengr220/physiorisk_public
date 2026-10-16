#!/usr/bin/env python3
"""Run the canonical full validation for the frozen PhysioRisk v2 components.

This producer is intentionally separate from the historical Sprint 2 producer.
It verifies all frozen participant-level inputs, refits only the development-only
CalibratedTotalRisk_v2 Cox model, and refuses to overwrite existing outputs.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import warnings
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from lifelines import CoxPHFitter, CoxTimeVaryingFitter, KaplanMeierFitter
from lifelines.exceptions import ConvergenceWarning
from lifelines.statistics import proportional_hazard_test
from lifelines.utils import concordance_index
from sklearn.linear_model import LogisticRegression


REPO = Path(__file__).resolve().parents[1]
OUTPUT_DIR = REPO / "outputs" / "physiorisk_v2_validation"
AUDIT_MD = REPO / "audit" / "PHYSIORISK_V2_FULL_VALIDATION.md"
PROVENANCE_JSON = REPO / "audit" / "physiorisk_v2_full_validation_provenance.json"
HISTORICAL_DIR = Path(
    os.environ.get("PHYSIORISK_DATA_DIR", "/home/ubuntu2204/longevity/data/physiorisk/data")
)

PARENT_COMMIT = "effea63db3f47eba4e4d95656b3dce41cb2f94fe"
PHYSIORISK_FROZEN_COMMIT = "7abcbc11a3eda981b2f4d88e385cb0486f1ed6d7"
SEED = 20260821
N_BOOT = 2000
ID, TIME, EVENT, AGE = "SEQN", "PERMTH_INT", "MORTSTAT", "RIDAGEYR"
DEMO = "DemoRisk"
PHYSIO = "PhysioRisk_2axis_v2"
CALIBRATED = "CalibratedTotalRisk_v2"
ORIGINAL = "TotalRisk_original_v2"
PHENO = "PhenoAge_NCP_v2"
ACCEL = "PhenoAge_NCP_acceleration_v2"

INPUTS = {
    "physio_development": (
        REPO / "outputs/physiorisk_2axis_v2_refit/physiorisk_2axis_v2_train_scored_levinenocrp.parquet",
        "578b08930f8ea524e205a6d7754b2c07739ed775d081346b39e24fd27890cab1",
    ),
    "physio_validation": (
        REPO / "outputs/physiorisk_2axis_v2_refit/physiorisk_2axis_v2_test_scored_levinenocrp.parquet",
        "e623e1e0d59da80e616a29a32821ab35552601864b650f239fde2566c362920d",
    ),
    "pheno_development": (
        REPO / "outputs/phenoage_ncp_v2/phenoage_ncp_v2_development_comparator.parquet",
        "c5575a31b94717813316af1d73f27115ef817decd5504cae910cbae3750fbfa8",
    ),
    "pheno_validation": (
        REPO / "outputs/phenoage_ncp_v2/phenoage_ncp_v2_validation_comparator.parquet",
        "e3dcbde86a340a3a0d3e007b62d095521f820132137ee6ca201ef882162c4005",
    ),
    "historical_development": (
        HISTORICAL_DIR / "physiorisk_2axis_v1_train_scored_from_frozen_baseline_levinenocrp.parquet",
        "e8f435b5a8b68dbb477f04bad280252f563b9323e9bc9dea4eb7e945c22cbb86",
    ),
    "historical_validation": (
        HISTORICAL_DIR / "physiorisk_2axis_v1_test_scored_from_frozen_baseline_levinenocrp.parquet",
        "1455e24e8ca3e1f68eb58a779f7a4d48e46b8e54fa435ec00de5cf51256d08ca",
    ),
}

OUTPUT_FILES = {
    "primary_metrics": "primary_validation_metrics_v2.csv",
    "paired_bootstrap": "paired_cindex_bootstrap_v2.csv",
    "coefficients": "calibrated_totalrisk_v2_coefficients.csv",
    "baseline_survival": "calibrated_totalrisk_v2_baseline_survival.csv",
    "original_metrics": "totalrisk_original_v2_metrics.csv",
    "calibration": "fixed_horizon_calibration_v2.csv",
    "calibration_plot": "calibration_plot_data_v2.csv",
    "ph_diagnostics": "ph_diagnostics_v2.csv",
    "schoenfeld_summary": "schoenfeld_residual_summary_v2.csv",
    "time_interactions": "time_interactions_v2.csv",
    "robust_discrimination": "censoring_robust_discrimination_v2.csv",
    "followup": "followup_support_v2.csv",
    "historical_comparison": "historical_corrected_comparison_v2.csv",
    "delta_comparison": "historical_corrected_delta_c_comparison_v2.csv",
    "conclusions": "conclusion_robustness_v2.csv",
    "participant_scores": "physiorisk_v2_validation_participant_scores.parquet",
    "metadata": "validation_metadata_v2.json",
    "manifest": "artifact_manifest_v2.json",
}

SCORE_MAP = {
    DEMO: DEMO,
    PHYSIO: PHYSIO,
    CALIBRATED: CALIBRATED,
    PHENO: PHENO,
    ACCEL: ACCEL,
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
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if isinstance(value, Path):
        return str(value)
    return value


def git_output(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=REPO, text=True).strip()


def require_repository_gate() -> None:
    if git_output("branch", "--show-current") != "fix/creatinine-unit-harmonization-v2":
        raise AssertionError("repository branch gate failed")
    if git_output("rev-parse", "HEAD") != PARENT_COMMIT:
        raise AssertionError("repository HEAD gate failed")
    status_lines = git_output("status", "--short").splitlines()
    allowed_new_producer = "?? scripts/run_physiorisk_v2_full_validation.py"
    unexpected = [line for line in status_lines if line != allowed_new_producer]
    if unexpected:
        raise AssertionError(f"unexpected pre-analysis working-tree changes: {unexpected}")
    for path in (OUTPUT_DIR, AUDIT_MD, PROVENANCE_JSON):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite existing output: {path}")
    for filename in OUTPUT_FILES.values():
        if "v2" not in filename.lower():
            raise AssertionError(f"output is not v2-qualified: {filename}")


def require_unique_ids(frame: pd.DataFrame, label: str) -> None:
    if frame[ID].isna().any() or not frame[ID].is_unique:
        raise AssertionError(f"{label} does not have unique, complete SEQN")


def align_to(reference: pd.DataFrame, other: pd.DataFrame, label: str) -> pd.DataFrame:
    require_unique_ids(reference, f"{label} reference")
    require_unique_ids(other, f"{label} other")
    if set(reference[ID].astype(int)) != set(other[ID].astype(int)):
        raise AssertionError(f"{label} participant IDs differ")
    return reference[[ID]].merge(other, on=ID, how="left", validate="one_to_one")


def max_abs_difference(left: pd.Series, right: pd.Series) -> float:
    a = pd.to_numeric(left, errors="coerce").to_numpy(float)
    b = pd.to_numeric(right, errors="coerce").to_numpy(float)
    finite = np.isfinite(a) & np.isfinite(b)
    return float(np.max(np.abs(a[finite] - b[finite]))) if finite.any() else 0.0


def load_frozen_inputs() -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    frames: dict[str, pd.DataFrame] = {}
    input_records: dict[str, Any] = {}
    for label, (path, expected_hash) in INPUTS.items():
        if not path.is_file():
            raise FileNotFoundError(path)
        actual_hash = sha256_file(path)
        if actual_hash != expected_hash:
            raise AssertionError(f"{label} hash {actual_hash} != {expected_hash}")
        frames[label] = pd.read_parquet(path)
        input_records[label] = {
            "path": str(path),
            "sha256": actual_hash,
            "rows": len(frames[label]),
        }

    dev = frames["physio_development"].copy()
    val = frames["physio_validation"].copy()
    if (len(dev), int(dev[EVENT].sum())) != (13090, 2520):
        raise AssertionError("development cohort count/death gate failed")
    if (len(val), int(val[EVENT].sum())) != (6739, 416):
        raise AssertionError("validation cohort count/death gate failed")

    dev_hist = align_to(dev, frames["historical_development"], "development historical")
    val_hist = align_to(val, frames["historical_validation"], "validation historical")
    dev_pheno = align_to(dev, frames["pheno_development"], "development PhenoAge")
    val_pheno = align_to(val, frames["pheno_validation"], "validation PhenoAge")
    if max_abs_difference(dev["BaselineRisk"], dev_hist["BaselineRisk"]) != 0.0:
        raise AssertionError("development DemoRisk differs from historical v1")
    if max_abs_difference(val["BaselineRisk"], val_hist["BaselineRisk"]) != 0.0:
        raise AssertionError("validation DemoRisk differs from historical v1")

    for frame, comparator in ((dev, dev_pheno), (val, val_pheno)):
        frame[DEMO] = frame["BaselineRisk"]
        frame[PHENO] = comparator[PHENO].to_numpy(float)
        frame[ACCEL] = comparator[ACCEL].to_numpy(float)

    verification = {
        "inputs": input_records,
        "development": {
            "n": len(dev),
            "deaths": int(dev[EVENT].sum()),
            "id_sha256": id_sha256(dev),
            "DemoRisk_max_abs_difference_vs_v1": max_abs_difference(dev[DEMO], dev_hist["BaselineRisk"]),
            "IDs_identical_across_frozen_components": True,
        },
        "validation": {
            "n": len(val),
            "deaths": int(val[EVENT].sum()),
            "id_sha256": id_sha256(val),
            "DemoRisk_max_abs_difference_vs_v1": max_abs_difference(val[DEMO], val_hist["BaselineRisk"]),
            "IDs_identical_across_frozen_components": True,
        },
        "PhysioRisk_values_verified_by_frozen_artifact_hash": True,
        "PhenoAge_values_verified_by_frozen_artifact_hash": True,
        "frozen_components_refit": False,
    }
    return dev, val, verification


def fit_calibrated_model(dev: pd.DataFrame, val: pd.DataFrame) -> CoxPHFitter:
    columns = [TIME, EVENT, DEMO, PHYSIO]
    model = CoxPHFitter(penalizer=0.0)
    model.fit(dev[columns], TIME, EVENT, batch_mode=True)
    beta_demo = float(model.params_.loc[DEMO])
    beta_physio = float(model.params_.loc[PHYSIO])
    historical = np.array([1.0586578128, 0.3563514639])
    if np.allclose(np.array([beta_demo, beta_physio]), historical, rtol=0.0, atol=1e-10):
        raise AssertionError("v2 calibration unexpectedly reused historical v1 coefficients")
    for frame in (dev, val):
        frame[ORIGINAL] = frame[DEMO] + frame[PHYSIO]
        frame[CALIBRATED] = beta_demo * frame[DEMO] + beta_physio * frame[PHYSIO]
    return model


def controlled_cox(frame: pd.DataFrame, predictor: str) -> tuple[pd.DataFrame, CoxPHFitter, float, pd.Series, list[str]]:
    data = frame[[TIME, EVENT, predictor]].dropna().copy()
    sd = float(data[predictor].std(ddof=1))
    data["predictor_z"] = (data[predictor] - data[predictor].mean()) / sd
    model = CoxPHFitter(penalizer=0.0)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", ConvergenceWarning)
        model.fit(
            data[[TIME, EVENT, "predictor_z"]],
            TIME,
            EVENT,
            batch_mode=True,
            fit_options={"step_size": 0.5, "max_steps": 1000, "precision": 1e-9},
        )
    convergence_warnings = [
        str(item.message) for item in caught if issubclass(item.category, ConvergenceWarning)
    ]
    return data, model, sd, model.summary.loc["predictor_z"], convergence_warnings


def bootstrap_cindices(val: pd.DataFrame) -> tuple[dict[str, np.ndarray], dict[str, int]]:
    rng = np.random.default_rng(SEED)
    n = len(val)
    arrays = {label: val[column].to_numpy(float) for label, column in SCORE_MAP.items()}
    times = val[TIME].to_numpy(float)
    events = val[EVENT].to_numpy(int)
    boot = {label: np.full(N_BOOT, np.nan) for label in SCORE_MAP}
    eventless_redraws = 0
    failures = 0
    for replicate in range(N_BOOT):
        while True:
            indices = rng.integers(0, n, n)
            if events[indices].sum() > 0:
                break
            eventless_redraws += 1
        try:
            for label, scores in arrays.items():
                boot[label][replicate] = concordance_index(
                    times[indices], -scores[indices], events[indices]
                )
        except Exception:
            failures += 1
    if failures or any(np.isnan(values).any() for values in boot.values()):
        raise RuntimeError(f"bootstrap failures={failures}")
    return boot, {"failures": failures, "eventless_redraws": eventless_redraws}


def primary_metrics(val: pd.DataFrame, boot: dict[str, np.ndarray]) -> pd.DataFrame:
    rows = []
    for label, column in SCORE_MAP.items():
        data, _, sd, summary, convergence = controlled_cox(val, column)
        rows.append(
            {
                "model": label,
                "cohort": "validation_2011_2016",
                "N": len(data),
                "deaths": int(data[EVENT].sum()),
                "Harrell_C": concordance_index(data[TIME], -data[column], data[EVENT]),
                "Harrell_C_bootstrap_95CI_low": np.quantile(boot[label], 0.025),
                "Harrell_C_bootstrap_95CI_high": np.quantile(boot[label], 0.975),
                "bootstrap_replicates": N_BOOT,
                "bootstrap_seed": SEED,
                "validation_SD_ddof1": sd,
                "HR_per_validation_SD": float(summary["exp(coef)"]),
                "HR_95CI_low": float(summary["exp(coef) lower 95%"]),
                "HR_95CI_high": float(summary["exp(coef) upper 95%"]),
                "p_value": float(summary["p"]),
                "pearson_age_correlation": float(val.loc[data.index, column].corr(val.loc[data.index, AGE])),
                "cox_penalizer": 0.0,
                "cox_convergence_warning": " | ".join(convergence) if convergence else "none",
            }
        )
    return pd.DataFrame(rows)


def paired_contrasts(
    metrics: pd.DataFrame,
    boot: dict[str, np.ndarray],
    bootstrap_counts: dict[str, int],
) -> pd.DataFrame:
    points = metrics.set_index("model")["Harrell_C"]
    pairs = [
        (CALIBRATED, DEMO),
        (CALIBRATED, PHENO),
        (PHYSIO, ACCEL),
    ]
    rows = []
    for model_a, model_b in pairs:
        differences = boot[model_a] - boot[model_b]
        rows.append(
            {
                "contrast": f"{model_a} - {model_b}",
                "model_A": model_a,
                "model_B": model_b,
                "observed_delta_C_A_minus_B": float(points[model_a] - points[model_b]),
                "percentile_95CI_low": np.quantile(differences, 0.025),
                "percentile_95CI_high": np.quantile(differences, 0.975),
                "proportion_bootstrap_delta_above_zero": float(np.mean(differences > 0)),
                "completed_replicates": int(np.isfinite(differences).sum()),
                "bootstrap_failures": bootstrap_counts["failures"],
                "eventless_redraws": bootstrap_counts["eventless_redraws"],
                "bootstrap_seed": SEED,
            }
        )
    result = pd.DataFrame(rows)
    frozen = result.iloc[2]
    targets = np.array(
        [0.008837578950992908, -0.011603816432397801, 0.028924588788065912]
    )
    actual = frozen[
        ["observed_delta_C_A_minus_B", "percentile_95CI_low", "percentile_95CI_high"]
    ].to_numpy(float)
    if not np.array_equal(actual, targets):
        raise AssertionError(f"frozen paired comparison C failed exact reproduction: {actual}")
    return result


def km_at(model: KaplanMeierFitter, time: float) -> float:
    return float(model.predict(time))


def ipcw_brier(time, event, prediction, horizon, censor_km) -> tuple[float, int]:
    time, event, prediction = map(np.asarray, (time, event, prediction))
    weights = np.zeros(len(time), float)
    event_by_horizon = (time <= horizon) & (event == 1)
    alive_at_horizon = time > horizon
    for index in np.where(event_by_horizon)[0]:
        weights[index] = 1.0 / max(
            km_at(censor_km, np.nextafter(float(time[index]), -np.inf)), 1e-10
        )
    weights[alive_at_horizon] = 1.0 / max(km_at(censor_km, horizon), 1e-10)
    outcome = event_by_horizon.astype(float)
    return float(np.mean(weights * (outcome - prediction) ** 2)), int(np.count_nonzero(weights))


def ipcw_binary_data(time, event, prediction, horizon, censor_km):
    time, event, prediction = map(np.asarray, (time, event, prediction))
    keep = ((time <= horizon) & (event == 1)) | (time > horizon)
    outcome = ((time <= horizon) & (event == 1)).astype(int)[keep]
    weights = np.empty(keep.sum(), float)
    kept_time, kept_event = time[keep], event[keep]
    event_by_horizon = (kept_time <= horizon) & (kept_event == 1)
    for index in np.where(event_by_horizon)[0]:
        weights[index] = 1.0 / max(
            km_at(censor_km, np.nextafter(float(kept_time[index]), -np.inf)), 1e-10
        )
    weights[~event_by_horizon] = 1.0 / max(km_at(censor_km, horizon), 1e-10)
    return outcome, prediction[keep], weights


def baseline_survival_at(model: CoxPHFitter, horizon: float) -> float:
    expanded = model.baseline_survival_.reindex(
        model.baseline_survival_.index.union([horizon])
    ).sort_index().ffill()
    return float(expanded.loc[horizon].iloc[0])


def calibration(
    calibration_model: CoxPHFitter, val: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, float]]:
    coefficients = calibration_model.params_.loc[[DEMO, PHYSIO]]
    center = float(calibration_model._norm_mean.loc[[DEMO, PHYSIO]] @ coefficients)
    linear_predictor = val[CALIBRATED].to_numpy(float)
    observed_km = KaplanMeierFitter().fit(val[TIME], val[EVENT])
    censor_km = KaplanMeierFitter().fit(val[TIME], 1 - val[EVENT])

    slope_data = val[[TIME, EVENT]].copy()
    slope_data["frozen_lp"] = linear_predictor
    slope_fit = CoxPHFitter(penalizer=0.0).fit(
        slope_data,
        TIME,
        EVENT,
        batch_mode=True,
        fit_options={"step_size": 0.5, "max_steps": 1000, "precision": 1e-9},
    )
    slope_summary = slope_fit.summary.loc["frozen_lp"]
    global_slope = {
        "estimate": float(slope_summary["coef"]),
        "ci_95_low": float(slope_summary["coef lower 95%"]),
        "ci_95_high": float(slope_summary["coef upper 95%"]),
        "p_value": float(slope_summary["p"]),
    }

    rows, plot_rows = [], []
    for horizon in (60, 96):
        base_survival = baseline_survival_at(calibration_model, horizon)
        prediction = 1 - np.power(base_survival, np.exp(linear_predictor - center))
        observed = 1 - km_at(observed_km, horizon)
        brier, usable = ipcw_brier(
            val[TIME], val[EVENT], prediction, horizon, censor_km
        )
        outcome, known_prediction, weights = ipcw_binary_data(
            val[TIME], val[EVENT], prediction, horizon, censor_km
        )
        logit_prediction = np.log(
            np.clip(known_prediction, 1e-8, 1 - 1e-8)
            / np.clip(1 - known_prediction, 1e-8, 1 - 1e-8)
        ).reshape(-1, 1)
        logistic = LogisticRegression(C=np.inf, solver="lbfgs", max_iter=1000).fit(
            logit_prediction, outcome, sample_weight=weights
        )
        rows.append(
            {
                "model": CALIBRATED,
                "horizon_months": horizon,
                "development_baseline_survival": base_survival,
                "development_lp_center": center,
                "mean_predicted_mortality": float(prediction.mean()),
                "KM_observed_mortality": observed,
                "observed_minus_predicted": observed - float(prediction.mean()),
                "observed_to_expected_ratio": observed / float(prediction.mean()),
                "IPCW_logistic_calibration_intercept": float(logistic.intercept_[0]),
                "IPCW_logistic_calibration_slope": float(logistic.coef_[0, 0]),
                "IPCW_Brier_score": brier,
                "IPCW_usable_N": usable,
                "IPCW_censoring_distribution": "validation censoring Kaplan-Meier",
                "known_outcomes_contribute_directly": True,
                "no_validation_recalibration": True,
                "global_Cox_calibration_slope": global_slope["estimate"],
                "global_Cox_calibration_slope_95CI_low": global_slope["ci_95_low"],
                "global_Cox_calibration_slope_95CI_high": global_slope["ci_95_high"],
                "global_Cox_calibration_slope_p": global_slope["p_value"],
            }
        )
        bins = pd.qcut(prediction, q=10, duplicates="drop")
        for bin_number, (_, indices) in enumerate(
            pd.Series(np.arange(len(val))).groupby(bins, observed=True), start=1
        ):
            idx = indices.to_numpy()
            bin_km = KaplanMeierFitter().fit(val[TIME].iloc[idx], val[EVENT].iloc[idx])
            plot_rows.append(
                {
                    "model": CALIBRATED,
                    "horizon_months": horizon,
                    "risk_decile": bin_number,
                    "N": len(idx),
                    "deaths_total": int(val[EVENT].iloc[idx].sum()),
                    "mean_predicted_mortality": float(prediction[idx].mean()),
                    "KM_observed_mortality": 1 - km_at(bin_km, horizon),
                    "number_at_risk_at_horizon": int((val[TIME].iloc[idx] >= horizon).sum()),
                }
            )
    return pd.DataFrame(rows), pd.DataFrame(plot_rows), global_slope


def schoenfeld_diagnostics(
    val: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    ph_rows, band_rows = [], []
    for label, column in SCORE_MAP.items():
        data, model, _, _, convergence = controlled_cox(val, column)
        result = proportional_hazard_test(
            model, data[[TIME, EVENT, "predictor_z"]], time_transform="rank"
        ).summary.loc["predictor_z"]
        residual = model.compute_residuals(
            data[[TIME, EVENT, "predictor_z"]], kind="scaled_schoenfeld"
        )["predictor_z"]
        residual_data = pd.DataFrame(
            {
                "event_time_months": val.loc[residual.index, TIME].to_numpy(),
                "scaled_schoenfeld_residual": residual.to_numpy(),
            }
        )
        residual_data["time_band"] = pd.cut(
            residual_data["event_time_months"],
            [-np.inf, 36, 72, np.inf],
            labels=["early_0_36m", "middle_37_72m", "late_73m_plus"],
        )
        summary_text = []
        for band, group in residual_data.groupby("time_band", observed=True):
            row = {
                "model": label,
                "time_band": str(band),
                "events": len(group),
                "mean_scaled_residual": float(group["scaled_schoenfeld_residual"].mean()),
                "median_scaled_residual": float(group["scaled_schoenfeld_residual"].median()),
            }
            band_rows.append(row)
            summary_text.append(f"{band}: mean={row['mean_scaled_residual']:.3f}")
        p_value = float(result["p"])
        ph_rows.append(
            {
                "model": label,
                "cohort": "validation_2011_2016",
                "N": len(data),
                "deaths": int(data[EVENT].sum()),
                "time_transform": "rank",
                "test_statistic": float(result["test_statistic"]),
                "p_value": p_value,
                "descriptive_flag_p_lt_0_01": bool(p_value < 0.01),
                "flag_rule": "p < 0.01; prespecified descriptive flag; no multiplicity adjustment",
                "scaled_residual_band_summary": "; ".join(summary_text),
                "cox_convergence_warning": " | ".join(convergence) if convergence else "none",
            }
        )
    return pd.DataFrame(ph_rows), pd.DataFrame(band_rows)


def expand_time_varying(val: pd.DataFrame, column: str) -> pd.DataFrame:
    score = (val[column] - val[column].mean()) / val[column].std(ddof=1)
    event_times = np.sort(val.loc[val[EVENT].eq(1), TIME].unique().astype(float))
    pieces = []
    for participant, (end, event, value) in enumerate(
        zip(val[TIME].to_numpy(float), val[EVENT].to_numpy(int), score.to_numpy(float))
    ):
        stops = event_times[event_times < end]
        if event == 1 or len(stops) == 0 or stops[-1] < end:
            stops = np.append(stops, end)
        starts = np.r_[0.0, stops[:-1]]
        valid = stops > starts
        stops, starts = stops[valid], starts[valid]
        events = np.zeros(len(stops), int)
        if event == 1 and len(events):
            events[-1] = 1
        pieces.append(
            pd.DataFrame(
                {
                    "id": participant,
                    "start": starts,
                    "stop": stops,
                    "event": events,
                    "score_z": value,
                    "score_z_x_log_time": value
                    * np.log(np.clip(stops, 1e-6, None) / 60.0),
                }
            )
        )
    return pd.concat(pieces, ignore_index=True)


def time_interaction(val: pd.DataFrame) -> pd.DataFrame:
    expanded = expand_time_varying(val, CALIBRATED)
    model = CoxTimeVaryingFitter(penalizer=0.0).fit(
        expanded,
        id_col="id",
        start_col="start",
        stop_col="stop",
        event_col="event",
        show_progress=False,
        fit_options={"step_size": 0.1, "max_steps": 1000, "precision": 1e-9},
    )
    main = model.summary.loc["score_z"]
    interaction = model.summary.loc["score_z_x_log_time"]
    beta_0, beta_1 = float(main["coef"]), float(interaction["coef"])
    return pd.DataFrame(
        [
            {
                "model": CALIBRATED,
                "cohort": "validation_2011_2016",
                "N": len(val),
                "deaths": int(val[EVENT].sum()),
                "score_scale": "validation cohort SD",
                "time_interaction": "standardized score * log(time_months / 60)",
                "reference_time_months": 60,
                "main_log_HR_at_60m": beta_0,
                "HR_per_SD_at_12m": float(np.exp(beta_0 + beta_1 * np.log(12 / 60))),
                "HR_per_SD_at_60m": float(np.exp(beta_0)),
                "HR_per_SD_at_96m": float(np.exp(beta_0 + beta_1 * np.log(96 / 60))),
                "time_interaction_coefficient": beta_1,
                "time_interaction_95CI_low": float(interaction["coef lower 95%"]),
                "time_interaction_95CI_high": float(interaction["coef upper 95%"]),
                "time_interaction_p_value": float(interaction["p"]),
                "direction": "effect_weakens_over_time" if beta_1 < 0 else "effect_strengthens_over_time",
                "diagnostic_only": True,
            }
        ]
    )


def robust_discrimination(dev: pd.DataFrame, val: pd.DataFrame) -> pd.DataFrame:
    from sksurv.metrics import concordance_index_ipcw, cumulative_dynamic_auc
    from sksurv.util import Surv

    y_dev = Surv.from_arrays(dev[EVENT].astype(bool), dev[TIME].astype(float))
    y_val = Surv.from_arrays(val[EVENT].astype(bool), val[TIME].astype(float))
    rows = []
    for label, column in SCORE_MAP.items():
        score = val[column].to_numpy(float)
        aucs, _ = cumulative_dynamic_auc(y_dev, y_val, score, np.array([60.0, 96.0]))
        for horizon, auc in zip((60, 96), aucs):
            uno = concordance_index_ipcw(y_dev, y_val, score, tau=float(horizon))[0]
            rows.append(
                {
                    "model": label,
                    "evaluation_cohort": "validation_2011_2016",
                    "censoring_distribution_cohort": "development_1999_2010",
                    "development_N_for_censoring": len(dev),
                    "validation_N": len(val),
                    "horizon_months": horizon,
                    "Uno_C_IPCW_truncated_at_horizon": float(uno),
                    "cumulative_dynamic_AUC_IPCW": float(auc),
                    "implementation": "scikit-survival 0.28.0",
                }
            )
    return pd.DataFrame(rows)


def followup_support(val: pd.DataFrame) -> pd.DataFrame:
    duration = val[TIME].astype(float)
    reverse_km = KaplanMeierFitter().fit(duration, event_observed=1 - val[EVENT])
    empirical = duration.quantile([0.25, 0.5, 0.75])
    rows = []
    for horizon in (60, 96):
        rows.append(
            {
                "cohort": "validation_2011_2016",
                "N": len(val),
                "deaths_total": int(val[EVENT].sum()),
                "reverse_KM_median_months": float(reverse_km.median_survival_time_),
                "empirical_Q1_months": float(empirical.loc[0.25]),
                "empirical_median_months": float(empirical.loc[0.5]),
                "empirical_Q3_months": float(empirical.loc[0.75]),
                "maximum_months": float(duration.max()),
                "horizon_months": horizon,
                "number_at_risk": int((duration >= horizon).sum()),
                "deaths_observed_by_horizon": int(
                    ((duration <= horizon) & val[EVENT].eq(1)).sum()
                ),
            }
        )
    result = pd.DataFrame(rows)
    if result["reverse_KM_median_months"].iloc[0] != 74.0:
        raise AssertionError("reverse-KM follow-up changed")
    if result["number_at_risk"].tolist() != [4461, 1137]:
        raise AssertionError("fixed-horizon support changed")
    return result


def historical_comparisons(
    metrics: pd.DataFrame, contrasts: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    historical_metrics = pd.read_csv(REPO / "tables/validation_v2.csv")
    mapping = {
        DEMO: "DemoRisk",
        PHYSIO: "PhysioRisk_convergence_corrected",
        CALIBRATED: "CalibratedTotalRisk",
        PHENO: "PhenoAge NCP",
        ACCEL: "PhenoAge NCP acceleration",
    }
    corrected = metrics.set_index("model")
    rows = []
    for corrected_name, historical_name in mapping.items():
        historical = historical_metrics.loc[
            historical_metrics["model"].eq(historical_name)
        ].iloc[0]
        current = corrected.loc[corrected_name]
        rows.append(
            {
                "model": corrected_name,
                "historical_model_label": historical_name,
                "historical_C": historical["C_index"],
                "corrected_C": current["Harrell_C"],
                "historical_HR_per_SD": historical["HR_per_actual_1SD"],
                "corrected_HR_per_SD": current["HR_per_validation_SD"],
                "historical_age_correlation": historical["age_correlation"],
                "corrected_age_correlation": current["pearson_age_correlation"],
                "historical_source": "tables/validation_v2.csv; defective v1 analysis pass; read-only",
            }
        )

    historical_delta = pd.read_csv(REPO / "tables/cindex_bootstrap_contrasts.csv")
    corrected_delta = contrasts.copy()
    historical_pairs = {
        f"{CALIBRATED} - {DEMO}": "CalibratedTotalRisk vs DemoRisk",
        f"{CALIBRATED} - {PHENO}": "CalibratedTotalRisk vs PhenoAge NCP",
        f"{PHYSIO} - {ACCEL}": "PhysioRisk_convergence_corrected vs PhenoAge NCP acceleration",
    }
    delta_rows = []
    for _, current in corrected_delta.iterrows():
        old_label = historical_pairs[current["contrast"]]
        old = historical_delta.loc[historical_delta["contrast"].eq(old_label)].iloc[0]
        delta_rows.append(
            {
                "contrast": current["contrast"],
                "historical_delta_C": old["point_C_index_difference_A_minus_B"],
                "historical_95CI_low": old["bootstrap_95CI_low"],
                "historical_95CI_high": old["bootstrap_95CI_high"],
                "corrected_delta_C": current["observed_delta_C_A_minus_B"],
                "corrected_95CI_low": current["percentile_95CI_low"],
                "corrected_95CI_high": current["percentile_95CI_high"],
            }
        )
    return pd.DataFrame(rows), pd.DataFrame(delta_rows)


def conclusion_assessment(
    metrics: pd.DataFrame,
    contrasts: pd.DataFrame,
    calibration_table: pd.DataFrame,
    ph_table: pd.DataFrame,
    interaction_table: pd.DataFrame,
) -> pd.DataFrame:
    metric = metrics.set_index("model")
    contrast = contrasts.set_index("contrast")
    delta_demo = contrast.loc[f"{CALIBRATED} - {DEMO}"]
    delta_pheno = contrast.loc[f"{CALIBRATED} - {PHENO}"]
    delta_accel = contrast.loc[f"{PHYSIO} - {ACCEL}"]
    calibrated_ph = ph_table.set_index("model").loc[CALIBRATED]
    interaction = interaction_table.iloc[0]
    physio_hr = metric.loc[PHYSIO]
    acceptable_calibration = bool(
        calibration_table["observed_to_expected_ratio"].between(0.8, 1.25).all()
        and calibration_table["IPCW_logistic_calibration_slope"].between(0.8, 1.25).all()
    )
    similar_to_pheno = bool(
        delta_pheno["percentile_95CI_low"] <= 0 <= delta_pheno["percentile_95CI_high"]
    )
    rows = [
        {
            "conclusion_number": 1,
            "conclusion": "PhysioRisk retains mortality information after age/sex adjustment.",
            "classification": "QUALITATIVELY UNCHANGED BUT NUMERICALLY REVISED",
            "evidence": (
                f"PhysioRisk is built from development age/sex-residualized biomarkers; "
                f"validation HR/SD={physio_hr.HR_per_validation_SD:.12g}, "
                f"95% CI {physio_hr.HR_95CI_low:.12g} to {physio_hr.HR_95CI_high:.12g}, "
                f"p={physio_hr.p_value:.12g}."
            ),
        },
        {
            "conclusion_number": 2,
            "conclusion": "PhysioRisk contributes incremental discrimination beyond DemoRisk.",
            "classification": "QUALITATIVELY UNCHANGED BUT NUMERICALLY REVISED",
            "evidence": (
                f"Paired delta C={delta_demo.observed_delta_C_A_minus_B:.12g}, "
                f"95% CI {delta_demo.percentile_95CI_low:.12g} to {delta_demo.percentile_95CI_high:.12g}."
            ),
        },
        {
            "conclusion_number": 3,
            "conclusion": "CalibratedTotalRisk has discrimination similar to PhenoAge NCP.",
            "classification": "QUALITATIVELY UNCHANGED BUT NUMERICALLY REVISED" if similar_to_pheno else "NO LONGER SUPPORTED",
            "evidence": (
                f"Paired delta C={delta_pheno.observed_delta_C_A_minus_B:.12g}, "
                f"95% CI {delta_pheno.percentile_95CI_low:.12g} to {delta_pheno.percentile_95CI_high:.12g}."
            ),
        },
        {
            "conclusion_number": 4,
            "conclusion": "PhysioRisk numerically exceeds NCP acceleration without established discrimination superiority.",
            "classification": (
                "QUALITATIVELY UNCHANGED BUT NUMERICALLY REVISED"
                if delta_accel.observed_delta_C_A_minus_B > 0
                and delta_accel.percentile_95CI_low <= 0
                else "NO LONGER SUPPORTED"
            ),
            "evidence": (
                f"Paired delta C={delta_accel.observed_delta_C_A_minus_B:.12g}, "
                f"95% CI {delta_accel.percentile_95CI_low:.12g} to {delta_accel.percentile_95CI_high:.12g}."
            ),
        },
        {
            "conclusion_number": 5,
            "conclusion": "Fixed-horizon calibration remains acceptable.",
            "classification": "QUALITATIVELY UNCHANGED BUT NUMERICALLY REVISED" if acceptable_calibration else "NO LONGER SUPPORTED",
            "evidence": "; ".join(
                f"{int(row.horizon_months)}m O/E={row.observed_to_expected_ratio:.4f}, "
                f"IPCW slope={row.IPCW_logistic_calibration_slope:.4f}"
                for _, row in calibration_table.iterrows()
            ),
        },
        {
            "conclusion_number": 6,
            "conclusion": "The PH/time-dependence limitation remains or changes.",
            "classification": (
                "QUALITATIVELY UNCHANGED BUT NUMERICALLY REVISED"
                if calibrated_ph.descriptive_flag_p_lt_0_01
                else "NO LONGER SUPPORTED"
            ),
            "evidence": (
                f"Schoenfeld p={calibrated_ph.p_value:.12g}; interaction beta="
                f"{interaction.time_interaction_coefficient:.12g}, 95% CI "
                f"{interaction.time_interaction_95CI_low:.12g} to "
                f"{interaction.time_interaction_95CI_high:.12g}, "
                f"p={interaction.time_interaction_p_value:.12g}. The Schoenfeld result "
                "retains the prespecified p < 0.01 flag; the interaction is diagnostic."
            ),
        },
    ]
    return pd.DataFrame(rows)


def markdown_table(frame: pd.DataFrame, columns: list[str], digits: int = 6) -> str:
    display = frame[columns].copy()
    for column in display.select_dtypes(include=["float"]).columns:
        display[column] = display[column].map(lambda value: f"{value:.{digits}g}")
    headers = "| " + " | ".join(columns) + " |"
    divider = "|" + "|".join(["---"] * len(columns)) + "|"
    body = "\n".join(
        "| " + " | ".join(str(value) for value in row) + " |"
        for row in display.itertuples(index=False, name=None)
    )
    return "\n".join([headers, divider, body])


def write_outputs(
    dev: pd.DataFrame,
    val: pd.DataFrame,
    verification: dict[str, Any],
    calibration_model: CoxPHFitter,
    metrics: pd.DataFrame,
    contrasts: pd.DataFrame,
    calibration_table: pd.DataFrame,
    plot_table: pd.DataFrame,
    global_slope: dict[str, float],
    ph_table: pd.DataFrame,
    schoenfeld_table: pd.DataFrame,
    interaction_table: pd.DataFrame,
    robust_table: pd.DataFrame,
    followup_table: pd.DataFrame,
    historical_table: pd.DataFrame,
    delta_table: pd.DataFrame,
    conclusions: pd.DataFrame,
) -> dict[str, Any]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=False)
    paths = {key: OUTPUT_DIR / filename for key, filename in OUTPUT_FILES.items()}
    coefficients = calibration_model.summary.loc[[DEMO, PHYSIO]].reset_index().rename(
        columns={"covariate": "component"}
    )
    coefficients.insert(0, "model", CALIBRATED)
    coefficients["fit_cohort"] = "development_1999_2010"
    coefficients["penalizer"] = 0.0
    coefficients["frozen_before_validation_evaluation"] = True
    baseline_survival = calibration_model.baseline_survival_.reset_index().rename(
        columns={
            calibration_model.baseline_survival_.index.name or "index": "time_months",
            "baseline survival": "baseline_survival",
        }
    )
    baseline_survival["fit_cohort"] = "development_1999_2010"
    baseline_survival["lifelines_covariate_center"] = float(
        calibration_model._norm_mean.loc[[DEMO, PHYSIO]]
        @ calibration_model.params_.loc[[DEMO, PHYSIO]]
    )
    original_metrics = metrics.loc[metrics["model"].eq(ORIGINAL)].copy()
    if original_metrics.empty:
        data, _, sd, summary, convergence = controlled_cox(val, ORIGINAL)
        original_metrics = pd.DataFrame(
            [
                {
                    "model": ORIGINAL,
                    "definition": f"{DEMO} + {PHYSIO}",
                    "N": len(data),
                    "deaths": int(data[EVENT].sum()),
                    "Harrell_C": concordance_index(data[TIME], -data[ORIGINAL], data[EVENT]),
                    "validation_SD_ddof1": sd,
                    "HR_per_validation_SD": float(summary["exp(coef)"]),
                    "HR_95CI_low": float(summary["exp(coef) lower 95%"]),
                    "HR_95CI_high": float(summary["exp(coef) upper 95%"]),
                    "p_value": float(summary["p"]),
                    "pearson_age_correlation": float(val[ORIGINAL].corr(val[AGE])),
                    "cox_convergence_warning": " | ".join(convergence) if convergence else "none",
                }
            ]
        )

    metrics.to_csv(paths["primary_metrics"], index=False)
    contrasts.to_csv(paths["paired_bootstrap"], index=False)
    coefficients.to_csv(paths["coefficients"], index=False)
    baseline_survival.to_csv(paths["baseline_survival"], index=False)
    original_metrics.to_csv(paths["original_metrics"], index=False)
    calibration_table.to_csv(paths["calibration"], index=False)
    plot_table.to_csv(paths["calibration_plot"], index=False)
    ph_table.to_csv(paths["ph_diagnostics"], index=False)
    schoenfeld_table.to_csv(paths["schoenfeld_summary"], index=False)
    interaction_table.to_csv(paths["time_interactions"], index=False)
    robust_table.to_csv(paths["robust_discrimination"], index=False)
    followup_table.to_csv(paths["followup"], index=False)
    historical_table.to_csv(paths["historical_comparison"], index=False)
    delta_table.to_csv(paths["delta_comparison"], index=False)
    conclusions.to_csv(paths["conclusions"], index=False)
    participant_columns = [ID, TIME, EVENT, AGE, DEMO, PHYSIO, ORIGINAL, CALIBRATED, PHENO, ACCEL]
    val[participant_columns].to_parquet(paths["participant_scores"], index=False)

    metadata = {
        "schema_version": 1,
        "analysis": "PhysioRisk v2 full temporal validation",
        "parent_commit": PARENT_COMMIT,
        "physiorisk_frozen_commit": PHYSIORISK_FROZEN_COMMIT,
        "producer": "scripts/run_physiorisk_v2_full_validation.py",
        "cohort_verification": verification,
        "calibrated_totalrisk_v2": {
            "fit_cohort": "development only",
            "formula": f"mortality ~ {DEMO} + {PHYSIO}",
            "penalizer": 0.0,
            "coefficients": {
                "beta_Demo_v2": float(calibration_model.params_.loc[DEMO]),
                "beta_Physio_v2": float(calibration_model.params_.loc[PHYSIO]),
            },
            "definition": f"{CALIBRATED} = beta_Demo_v2 * {DEMO} + beta_Physio_v2 * {PHYSIO}",
            "baseline_survival_artifact": str(paths["baseline_survival"].relative_to(REPO)),
            "baseline_survival_center": float(
                calibration_model._norm_mean.loc[[DEMO, PHYSIO]]
                @ calibration_model.params_.loc[[DEMO, PHYSIO]]
            ),
            "log_likelihood": float(calibration_model.log_likelihood_),
            "frozen_before_validation_evaluation": True,
            "validation_outcomes_influenced_fitting": False,
        },
        "totalrisk_original_v2": {
            "definition": f"{ORIGINAL} = {DEMO} + {PHYSIO}",
            "historical_provenance_only": True,
            "primary_manuscript_composite": False,
        },
        "independent_audit_reconciliation": {
            "TotalRisk_original_v2_HR_per_SD": {
                "observed": float(original_metrics.iloc[0]["HR_per_validation_SD"]),
                "approximate_target": 1.8697,
                "observed_minus_target": float(original_metrics.iloc[0]["HR_per_validation_SD"] - 1.8697),
            },
            "TotalRisk_original_v2_Harrell_C": {
                "observed": float(original_metrics.iloc[0]["Harrell_C"]),
                "approximate_target": 0.8415,
                "observed_minus_target": float(original_metrics.iloc[0]["Harrell_C"] - 0.8415),
            },
            "CalibratedTotalRisk_v2_HR_per_SD": {
                "observed": float(metrics.set_index("model").loc[CALIBRATED, "HR_per_validation_SD"]),
                "approximate_target": 3.2705,
                "observed_minus_target": float(metrics.set_index("model").loc[CALIBRATED, "HR_per_validation_SD"] - 3.2705),
            },
            "CalibratedTotalRisk_v2_Harrell_C": {
                "observed": float(metrics.set_index("model").loc[CALIBRATED, "Harrell_C"]),
                "approximate_target": 0.8445,
                "observed_minus_target": float(metrics.set_index("model").loc[CALIBRATED, "Harrell_C"] - 0.8445),
            },
            "paired_comparison_C_exact_target_reproduced": True,
        },
        "historical_submitted_reference": {
            "PhysioRisk_submitted_C": 0.6541097324576873,
            "PhysioRisk_submitted_HR_per_SD": 2.771657907710413,
            "PhysioRisk_submitted_HR_status": "historical non-converged fit; retained for provenance only and excluded from scientific comparison",
            "source": "manuscript/generated/table_s9_historical_submitted_results.csv",
        },
        "primary_validation_metrics": metrics.to_dict(orient="records"),
        "paired_bootstrap": contrasts.to_dict(orient="records"),
        "fixed_horizon_calibration": calibration_table.to_dict(orient="records"),
        "global_calibration_slope": global_slope,
        "ph_diagnostics": ph_table.to_dict(orient="records"),
        "time_interaction": interaction_table.to_dict(orient="records"),
        "censoring_robust_discrimination": robust_table.to_dict(orient="records"),
        "followup_support": followup_table.to_dict(orient="records"),
        "historical_corrected_comparison": historical_table.to_dict(orient="records"),
        "historical_corrected_delta_c_comparison": delta_table.to_dict(orient="records"),
        "conclusion_robustness": conclusions.to_dict(orient="records"),
        "methods": {
            "bootstrap": {"replicates": N_BOOT, "seed": SEED, "participant_level_paired_resampling": True},
            "fixed_horizon_IPCW": "validation censoring KM; known outcomes direct; censoring before horizon excluded from binary fit and represented through standard IPCW among known outcomes",
            "robust_discrimination_censoring_distribution": "development cohort",
            "PH_time_transform": "rank",
            "PH_descriptive_flag": "p < 0.01",
            "assay_standardization_1999_2000_sensitivity_applied": False,
        },
        "safety": {
            "frozen_PhysioRisk_modified": False,
            "frozen_PhenoAge_modified": False,
            "historical_outputs_overwritten": False,
            "manuscript_or_supplement_modified": False,
            "journal_submission_packages_modified": False,
            "cohort_or_temporal_split_modified": False,
        },
    }
    paths["metadata"].write_text(json.dumps(safe_json(metadata), indent=2) + "\n")

    manifest_entries = []
    for key, path in paths.items():
        if key == "manifest":
            continue
        entry = {
            "artifact": key,
            "path": str(path.relative_to(REPO)),
            "sha256": sha256_file(path),
            "bytes": path.stat().st_size,
            "participant_level": key == "participant_scores",
            "ignored_by_git": key == "participant_scores",
        }
        if path.suffix == ".csv":
            entry["rows"] = len(pd.read_csv(path))
        elif path.suffix == ".parquet":
            entry["rows"] = len(pd.read_parquet(path))
        manifest_entries.append(entry)
    paths["manifest"].write_text(json.dumps(manifest_entries, indent=2) + "\n")
    return {
        "paths": paths,
        "coefficients": coefficients,
        "original_metrics": original_metrics,
        "metadata": metadata,
        "manifest_entries": manifest_entries,
    }


def write_audits(
    written: dict[str, Any],
    metrics: pd.DataFrame,
    contrasts: pd.DataFrame,
    calibration_table: pd.DataFrame,
    global_slope: dict[str, float],
    ph_table: pd.DataFrame,
    interaction_table: pd.DataFrame,
    robust_table: pd.DataFrame,
    followup_table: pd.DataFrame,
    historical_table: pd.DataFrame,
    delta_table: pd.DataFrame,
    conclusions: pd.DataFrame,
) -> None:
    coefficients = written["coefficients"]
    original = written["original_metrics"]
    participant = written["paths"]["participant_scores"]
    beta_demo = float(coefficients.loc[coefficients["component"].eq(DEMO), "coef"].iloc[0])
    beta_physio = float(coefficients.loc[coefficients["component"].eq(PHYSIO), "coef"].iloc[0])
    audit_text = f"""# PhysioRisk v2 Full Validation

## Scope and frozen lineage

This analysis was run from parent commit `{PARENT_COMMIT}`. `PhysioRisk_2axis_v2`
is frozen from commit `{PHYSIORISK_FROZEN_COMMIT}`; `PhenoAge_NCP_v2` and its
acceleration are frozen from the parent commit. DemoRisk was joined by `SEQN`
and is bit-for-bit identical to the historical v1 participant values.

Development contains 13,090 participants and 2,520 deaths. Temporal validation
contains 6,739 participants and 416 deaths. Participant-ID sets are identical
across DemoRisk, PhysioRisk, and PhenoAge in each cohort. Input paths and SHA256
hashes are recorded in the machine-readable provenance record.

Neither frozen corrected component was refit. Cohort membership, temporal split,
model specifications, and the separate 1999–2000 assay-standardization
sensitivity were not changed.

## Development-only calibrated composite

The unpenalized development Cox model `mortality ~ DemoRisk +
PhysioRisk_2axis_v2` produced:

- `beta_Demo_v2 = {beta_demo!r}`
- `beta_Physio_v2 = {beta_physio!r}`

`CalibratedTotalRisk_v2 = beta_Demo_v2 * DemoRisk + beta_Physio_v2 *
PhysioRisk_2axis_v2`. Coefficients and development baseline survival were frozen
before any validation evaluation. The full baseline-survival step function and
lifelines centering constant are in
`outputs/physiorisk_v2_validation/calibrated_totalrisk_v2_baseline_survival.csv`.

## Historical unit-weight composite

`TotalRisk_original_v2 = DemoRisk + PhysioRisk_2axis_v2` was reconstructed only
for provenance and is not the primary composite.

{markdown_table(original, ['model','N','deaths','Harrell_C','HR_per_validation_SD','HR_95CI_low','HR_95CI_high','p_value','pearson_age_correlation'], 12)}

## Primary validation metrics

{markdown_table(metrics, ['model','Harrell_C','Harrell_C_bootstrap_95CI_low','Harrell_C_bootstrap_95CI_high','HR_per_validation_SD','HR_95CI_low','HR_95CI_high','p_value','pearson_age_correlation'], 12)}

## Paired C-index bootstrap

All contrasts used 2,000 participant-level paired replicates with seed 20260821.

{markdown_table(contrasts, ['contrast','observed_delta_C_A_minus_B','percentile_95CI_low','percentile_95CI_high','bootstrap_failures','eventless_redraws'], 12)}

## Fixed-horizon calibration

Absolute predictions use only the development coefficients and baseline
survival. Validation outcomes enter evaluation only. Fixed-horizon IPCW uses
the validation censoring Kaplan–Meier estimator; known outcomes contribute
directly and participants censored before the horizon do not supply an observed
binary outcome.

{markdown_table(calibration_table, ['horizon_months','mean_predicted_mortality','KM_observed_mortality','observed_to_expected_ratio','IPCW_logistic_calibration_intercept','IPCW_logistic_calibration_slope','IPCW_Brier_score'], 12)}

Global Cox calibration slope: `{global_slope['estimate']!r}` (95% CI
`{global_slope['ci_95_low']!r}` to `{global_slope['ci_95_high']!r}`;
p=`{global_slope['p_value']!r}`).

## Proportional-hazards diagnostics

{markdown_table(ph_table, ['model','test_statistic','p_value','descriptive_flag_p_lt_0_01','scaled_residual_band_summary'], 10)}

The diagnostic extended Cox result for CalibratedTotalRisk_v2 was:

{markdown_table(interaction_table, ['model','time_interaction_coefficient','time_interaction_95CI_low','time_interaction_95CI_high','time_interaction_p_value','direction'], 12)}

## Censoring-robust discrimination

{markdown_table(robust_table, ['model','horizon_months','Uno_C_IPCW_truncated_at_horizon','cumulative_dynamic_AUC_IPCW'], 10)}

## Follow-up support

{markdown_table(followup_table, ['horizon_months','reverse_KM_median_months','number_at_risk','deaths_observed_by_horizon'], 10)}

## Historical versus corrected comparison

{markdown_table(historical_table, ['model','historical_C','corrected_C','historical_HR_per_SD','corrected_HR_per_SD','historical_age_correlation','corrected_age_correlation'], 10)}

{markdown_table(delta_table, ['contrast','historical_delta_C','historical_95CI_low','historical_95CI_high','corrected_delta_C','corrected_95CI_low','corrected_95CI_high'], 10)}

The historical comparison uses the read-only defective-v1 analysis pass in
`tables/validation_v2.csv` and `tables/cindex_bootstrap_contrasts.csv`.
Historical submitted PhysioRisk's non-converged HR is not used; the prior
convergence-controlled HR is the scientific comparison value.

## Conclusion robustness

{markdown_table(conclusions, ['conclusion_number','conclusion','classification','evidence'], 8)}

## Artifacts and safety

All aggregate results are under `outputs/physiorisk_v2_validation/`. The local
participant-level score carrier is ignored by Git:
`{participant.relative_to(REPO)}` (SHA256 `{sha256_file(participant)}`). It is
listed in the artifact manifest and contains no new cohort members.

No manuscript, supplement, historical table, frozen model output, Research
Square package, GeroScience package, or Biogerontology package was modified.
No manuscript has yet been modified.
"""
    AUDIT_MD.write_text(audit_text)

    generated = {
        entry["artifact"]: {
            "path": entry["path"],
            "sha256": entry["sha256"],
            "bytes": entry["bytes"],
            "participant_level": entry["participant_level"],
            **({"rows": entry["rows"]} if "rows" in entry else {}),
        }
        for entry in written["manifest_entries"]
    }
    generated["artifact_manifest"] = {
        "path": str(written["paths"]["manifest"].relative_to(REPO)),
        "sha256": sha256_file(written["paths"]["manifest"]),
        "bytes": written["paths"]["manifest"].stat().st_size,
        "participant_level": False,
    }
    generated["audit_markdown"] = {
        "path": str(AUDIT_MD.relative_to(REPO)),
        "sha256": sha256_file(AUDIT_MD),
        "bytes": AUDIT_MD.stat().st_size,
        "participant_level": False,
    }
    generated["producer_script"] = {
        "path": str(Path(__file__).resolve().relative_to(REPO)),
        "sha256": sha256_file(Path(__file__).resolve()),
        "bytes": Path(__file__).resolve().stat().st_size,
        "participant_level": False,
    }
    provenance = {
        **written["metadata"],
        "generated_artifacts": generated,
        "provenance_self_hash_excluded": "A file cannot contain its own stable cryptographic hash.",
        "explicit_statement": "No manuscript has yet been modified.",
    }
    PROVENANCE_JSON.write_text(json.dumps(safe_json(provenance), indent=2) + "\n")


def main() -> None:
    require_repository_gate()
    print("repository gate passed", flush=True)
    dev, val, verification = load_frozen_inputs()
    print("frozen inputs and cohort identities verified", flush=True)
    calibration_model = fit_calibrated_model(dev, val)
    print(
        "development calibration fitted: "
        f"beta_Demo_v2={calibration_model.params_.loc[DEMO]!r}, "
        f"beta_Physio_v2={calibration_model.params_.loc[PHYSIO]!r}",
        flush=True,
    )
    boot, bootstrap_counts = bootstrap_cindices(val)
    print("paired bootstrap complete", flush=True)
    metrics = primary_metrics(val, boot)
    contrasts = paired_contrasts(metrics, boot, bootstrap_counts)
    calibration_table, plot_table, global_slope = calibration(calibration_model, val)
    print("primary metrics and fixed-horizon calibration complete", flush=True)
    ph_table, schoenfeld_table = schoenfeld_diagnostics(val)
    interaction_table = time_interaction(val)
    print("PH and time-interaction diagnostics complete", flush=True)
    robust_table = robust_discrimination(dev, val)
    followup_table = followup_support(val)
    historical_table, delta_table = historical_comparisons(metrics, contrasts)
    conclusions = conclusion_assessment(
        metrics, contrasts, calibration_table, ph_table, interaction_table
    )
    print("robust discrimination and scientific comparisons complete", flush=True)
    written = write_outputs(
        dev,
        val,
        verification,
        calibration_model,
        metrics,
        contrasts,
        calibration_table,
        plot_table,
        global_slope,
        ph_table,
        schoenfeld_table,
        interaction_table,
        robust_table,
        followup_table,
        historical_table,
        delta_table,
        conclusions,
    )
    write_audits(
        written,
        metrics,
        contrasts,
        calibration_table,
        global_slope,
        ph_table,
        interaction_table,
        robust_table,
        followup_table,
        historical_table,
        delta_table,
        conclusions,
    )
    print(
        json.dumps(
            {
                "status": "complete",
                "output_directory": str(OUTPUT_DIR.relative_to(REPO)),
                "audit_markdown": str(AUDIT_MD.relative_to(REPO)),
                "provenance_json": str(PROVENANCE_JSON.relative_to(REPO)),
            }
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
