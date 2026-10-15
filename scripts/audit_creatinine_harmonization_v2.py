#!/usr/bin/env python3
"""Audit staged PhysioRisk creatinine harmonization without fitting models."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from patsy import dmatrix
from sklearn.linear_model import LinearRegression


REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.creatinine_unit_contract_v2 import (  # noqa: E402
    CREATININE_CONTRACTS,
    contract_dataframe,
    harmonize_creatinine,
)


DEFAULT_HISTORICAL_DIR = Path("/home/ubuntu2204/longevity/data/physiorisk/data")
CONTRACT_CSV = REPO / "audit/creatinine_unit_contract_v2.csv"
HISTORICAL_HASHES = {
    "benchmark_levine_no_crp_cohort.parquet": (
        "f53d03317a6ea123021e7e36d585f7d92ba6f198821f21b083adfcc4b8e87125"
    ),
    "physiorisk_2axis_v1_train_scored_from_frozen_baseline_levinenocrp.parquet": (
        "e8f435b5a8b68dbb477f04bad280252f563b9323e9bc9dea4eb7e945c22cbb86"
    ),
    "physiorisk_2axis_v1_test_scored_from_frozen_baseline_levinenocrp.parquet": (
        "1455e24e8ca3e1f68eb58a779f7a4d48e46b8e54fa435ec00de5cf51256d08ca"
    ),
}
EXPECTED_COUNTS = {
    "development_n": 13090,
    "development_deaths": 2520,
    "validation_n": 6739,
    "validation_deaths": 416,
    "changed_development_participants": 2217,
}
TARGETS = {
    "old_residual_sd": (33.1786, 0.0005),
    "corrected_residual_sd": (0.3601, 0.0005),
    "old_cycle_indicator_correlation": (0.8807, 0.0005),
    "corrected_cycle_indicator_correlation": (0.0421, 0.0005),
    "old_cycle_indicator_r_squared": (0.7756, 0.0005),
    "corrected_cycle_indicator_r_squared": (0.0018, 0.0005),
    "old_affected_cycle_median": (79.56, 0.0051),
    "corrected_affected_cycle_median": (0.90, 0.0051),
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def require_file(path: Path) -> Path:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path


def assert_unique_ids(frame: pd.DataFrame, label: str) -> None:
    if frame["SEQN"].isna().any() or not frame["SEQN"].is_unique:
        raise AssertionError(f"{label} does not have unique, nonmissing SEQN")


def compare_id_sets(current: pd.DataFrame, historical: pd.DataFrame, label: str) -> dict:
    assert_unique_ids(current, f"staged {label}")
    assert_unique_ids(historical, f"historical {label}")
    current_ids = set(current["SEQN"].astype(int))
    historical_ids = set(historical["SEQN"].astype(int))
    missing = historical_ids - current_ids
    added = current_ids - historical_ids
    if missing or added:
        raise AssertionError(
            f"{label} participant IDs differ: missing={len(missing)}, added={len(added)}"
        )
    return {
        "identical": True,
        "n": len(current_ids),
        "missing_from_staged": 0,
        "added_in_staged": 0,
    }


def assert_numeric_equal(
    left: pd.Series,
    right: pd.Series,
    label: str,
    *,
    atol: float = 0.0,
) -> None:
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


def creatinine_residual_diagnostics(frame: pd.DataFrame) -> dict[str, float]:
    ordered = frame.sort_values("SEQN").reset_index(drop=True)
    design = dmatrix(
        "cr(RIDAGEYR, df=4) + RIAGENDR", ordered, return_type="dataframe"
    )
    values = ordered["LBXSCR"].to_numpy(dtype=float)
    residuals = values - LinearRegression().fit(design, values).predict(design)
    indicator = ordered["cycle_start_year"].eq(2001).astype(float).to_numpy()
    correlation = float(np.corrcoef(residuals, indicator)[0, 1])
    indicator_model = LinearRegression().fit(indicator.reshape(-1, 1), residuals)
    return {
        "residual_sd": float(np.std(residuals, ddof=0)),
        "cycle_indicator_correlation": correlation,
        "cycle_indicator_r_squared": float(
            indicator_model.score(indicator.reshape(-1, 1), residuals)
        ),
        "affected_cycle_median": float(
            ordered.loc[ordered["cycle_start_year"].eq(2001), "LBXSCR"].median()
        ),
    }


def verify_contract_csv() -> None:
    committed = pd.read_csv(CONTRACT_CSV).fillna("")
    generated = contract_dataframe().fillna("")
    pd.testing.assert_frame_equal(
        committed.reset_index(drop=True),
        generated.reset_index(drop=True),
        check_dtype=False,
    )


def verify_source_contract(stage: Path, master: pd.DataFrame) -> list[dict]:
    reconciliations = []
    for cycle, contract in CREATININE_CONTRACTS.items():
        folder = cycle.split("-", 1)[0]
        chemistry_path = require_file(
            stage / "inputs" / folder / contract.chemistry_source_file
        )
        chemistry = pd.read_sas(chemistry_path, format="xport")
        expected = harmonize_creatinine(
            chemistry, cycle, contract.chemistry_source_file
        )
        route = dict(expected.attrs)
        observed = master.loc[master["CYCLE"].eq(cycle), ["SEQN", "LBXSCR"]]
        comparison = expected.merge(
            observed,
            on="SEQN",
            how="left",
            suffixes=("_expected", "_staged"),
            validate="one_to_one",
        )
        assert_numeric_equal(
            comparison["LBXSCR_expected"],
            comparison["LBXSCR_staged"],
            f"{cycle} staged canonical creatinine",
        )
        if route["canonical_unit"] != "mg/dL":
            raise AssertionError(f"{cycle} canonical unit is not mg/dL")
        if route["selected_source_variable"] != contract.selected_source_variable:
            raise AssertionError(
                f"{cycle} selected {route['selected_source_variable']} instead of "
                f"{contract.selected_source_variable}"
            )
        route["paired_max_abs_difference_mg_dL"] = (
            None
            if not np.isfinite(route["paired_max_abs_difference_mg_dL"])
            else route["paired_max_abs_difference_mg_dL"]
        )
        reconciliations.append(route)

        if cycle == "2001-2002":
            fallback_input = chemistry.drop(columns=["LBDSCR"])
            fallback = harmonize_creatinine(
                fallback_input, cycle, contract.chemistry_source_file
            )
            if fallback.attrs["selected_source_variable"] != "LBDSCRSI":
                raise AssertionError("2001-2002 SI fallback route did not activate")
            assert_numeric_equal(
                fallback["LBXSCR"],
                pd.to_numeric(fallback_input["LBDSCRSI"], errors="coerce") / 88.4,
                "2001-2002 SI fallback conversion",
            )
    return reconciliations


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--staging-dir", type=Path, required=True)
    parser.add_argument(
        "--historical-dir", type=Path, default=DEFAULT_HISTORICAL_DIR
    )
    args = parser.parse_args()
    stage = args.staging_dir.resolve()
    historical_dir = args.historical_dir.resolve()
    outputs = stage / "outputs"

    verify_contract_csv()
    for filename, expected_hash in HISTORICAL_HASHES.items():
        path = require_file(historical_dir / filename)
        actual_hash = sha256_file(path)
        if actual_hash != expected_hash:
            raise AssertionError(
                f"historical artifact hash mismatch for {filename}: {actual_hash}"
            )

    master = pd.read_parquet(
        require_file(outputs / "nhanes_biomarker_master_verified.parquet")
    )
    benchmark = pd.read_parquet(
        require_file(outputs / "benchmark_levine_no_crp_cohort.parquet")
    )
    development = pd.read_parquet(require_file(outputs / "development_cohort.parquet"))
    validation = pd.read_parquet(require_file(outputs / "validation_cohort.parquet"))
    old_benchmark = pd.read_parquet(
        historical_dir / "benchmark_levine_no_crp_cohort.parquet"
    )
    old_development = pd.read_parquet(
        historical_dir
        / "physiorisk_2axis_v1_train_scored_from_frozen_baseline_levinenocrp.parquet"
    )
    old_validation = pd.read_parquet(
        historical_dir
        / "physiorisk_2axis_v1_test_scored_from_frozen_baseline_levinenocrp.parquet"
    )

    identity = {
        "benchmark": compare_id_sets(benchmark, old_benchmark, "benchmark"),
        "development": compare_id_sets(development, old_development, "development"),
        "validation": compare_id_sets(validation, old_validation, "validation"),
    }

    observed_counts = {
        "development_n": len(development),
        "development_deaths": int(development["MORTSTAT"].sum()),
        "validation_n": len(validation),
        "validation_deaths": int(validation["MORTSTAT"].sum()),
    }
    for name, expected in EXPECTED_COUNTS.items():
        if name != "changed_development_participants" and observed_counts[name] != expected:
            raise AssertionError(f"{name}={observed_counts[name]} != {expected}")

    benchmark_comparison = old_benchmark.merge(
        benchmark,
        on="SEQN",
        how="inner",
        suffixes=("_old", "_corrected"),
        validate="one_to_one",
    )
    unaffected = benchmark_comparison["cycle_start_year_old"].ne(2001)
    assert_numeric_equal(
        benchmark_comparison.loc[unaffected, "LBXSCR_old"],
        benchmark_comparison.loc[unaffected, "LBXSCR_corrected"],
        "creatinine in cycles other than 2001-2002",
    )

    unchanged_columns = [
        column
        for column in old_benchmark.columns
        if column != "LBXSCR" and column in benchmark.columns and column != "SEQN"
    ]
    for column in unchanged_columns:
        assert_numeric_equal(
            benchmark_comparison[f"{column}_old"],
            benchmark_comparison[f"{column}_corrected"],
            f"unchanged benchmark column {column}",
        )

    development_comparison = old_development.merge(
        development,
        on="SEQN",
        how="inner",
        suffixes=("_old", "_corrected"),
        validate="one_to_one",
    )
    changed = ~np.isclose(
        development_comparison["LBXSCR_old"].to_numpy(dtype=float),
        development_comparison["LBXSCR_corrected"].to_numpy(dtype=float),
        rtol=0.0,
        atol=1e-12,
        equal_nan=True,
    )
    changed_n = int(changed.sum())
    if changed_n != EXPECTED_COUNTS["changed_development_participants"]:
        raise AssertionError(f"changed development participants={changed_n} != 2217")
    changed_cycles = set(
        development_comparison.loc[changed, "cycle_start_year_old"].astype(int)
    )
    if changed_cycles != {2001}:
        raise AssertionError(f"creatinine changed outside 2001-2002: {changed_cycles}")

    reconciliations = verify_source_contract(stage, master)
    old_diagnostics = creatinine_residual_diagnostics(old_development)
    corrected_diagnostics = creatinine_residual_diagnostics(development)
    observed_targets = {
        "old_residual_sd": old_diagnostics["residual_sd"],
        "corrected_residual_sd": corrected_diagnostics["residual_sd"],
        "old_cycle_indicator_correlation": old_diagnostics[
            "cycle_indicator_correlation"
        ],
        "corrected_cycle_indicator_correlation": corrected_diagnostics[
            "cycle_indicator_correlation"
        ],
        "old_cycle_indicator_r_squared": old_diagnostics[
            "cycle_indicator_r_squared"
        ],
        "corrected_cycle_indicator_r_squared": corrected_diagnostics[
            "cycle_indicator_r_squared"
        ],
        "old_affected_cycle_median": old_diagnostics["affected_cycle_median"],
        "corrected_affected_cycle_median": corrected_diagnostics[
            "affected_cycle_median"
        ],
    }
    target_results = {}
    for name, observed in observed_targets.items():
        expected, tolerance = TARGETS[name]
        difference = abs(observed - expected)
        target_results[name] = {
            "observed": observed,
            "expected_approximately": expected,
            "absolute_difference": difference,
            "absolute_tolerance": tolerance,
            "reconciles": difference <= tolerance,
        }
    all_targets_reconcile = all(
        result["reconciles"] for result in target_results.values()
    )
    if not all_targets_reconcile:
        failed = [name for name, result in target_results.items() if not result["reconciles"]]
        raise AssertionError(f"independent numerical targets did not reconcile: {failed}")

    result = {
        "status": "pass",
        "canonical_creatinine_unit": "mg/dL",
        "actual_2001_2002_route": "LBDSCR direct (mg/dL)",
        "approved_2001_2002_fallback": "LBDSCRSI / 88.4",
        "source_reconciliation_by_cycle": reconciliations,
        "participant_identity": identity,
        "counts": {
            **observed_counts,
            "changed_development_participants": changed_n,
        },
        "other_cycles_creatinine_unchanged": True,
        "other_benchmark_fields_unchanged": True,
        "old_diagnostics": old_diagnostics,
        "corrected_diagnostics": corrected_diagnostics,
        "target_reconciliation": target_results,
        "all_independent_targets_reconcile": all_targets_reconcile,
        "models_refit": False,
    }

    audit_dir = stage / "audit"
    report_path = audit_dir / "creatinine_harmonization_audit_v2.json"
    if report_path.exists():
        raise FileExistsError(f"refusing to overwrite audit report: {report_path}")
    audit_dir.mkdir(parents=False, exist_ok=False)
    report_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({**result, "report_path": str(report_path)}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
