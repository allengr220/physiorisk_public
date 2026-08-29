#!/usr/bin/env python3
"""Re-execute the canonical notebook-05 comparison cells and export Table 2."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import nbformat
import pandas as pd


REPO = Path(__file__).resolve().parents[1]
NOTEBOOK = REPO / "notebooks/05_physiorisk_model_validation.ipynb"

SUBMITTED = pd.DataFrame([
    ("BaselineRisk", 0.827, 3.74, 3.35, 4.17, 0.97),
    ("PhysioRisk_2axis", 0.654, 2.77, 2.66, 2.89, 0.11),
    ("TotalRisk_2axis", 0.840, 1.88, 1.82, 1.94, 0.81),
    ("PhenoAge_noCRP_proxy", 0.841, 3.98, 3.64, 4.35, 0.96),
    ("PhenoAgeAccel", 0.638, 1.43, 1.36, 1.51, 0.03),
], columns=["risk_score", "C_index", "HR_per_1SD", "HR_95CI_low", "HR_95CI_high", "corr_age"])


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", type=Path, required=True)
    parser.add_argument("--test", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)

    nb = nbformat.read(NOTEBOOK, as_version=4)
    ns: dict = {"Path": Path}
    # Execute the canonical imports, definitions, comparator construction,
    # evaluation helpers, and benchmark table cells without Colab mounting.
    exec(nb.cells[2].source, ns)
    config = nb.cells[5].source.replace(
        'Path("/content/drive/MyDrive/LRE/data/pub/physiorisk_2axis_v1_train_scored_from_frozen_baseline_levinenocrp.parquet")',
        f'Path({str(args.train.resolve())!r})',
    ).replace(
        'Path("/content/drive/MyDrive/LRE/data/pub/physiorisk_2axis_v1_test_scored_from_frozen_baseline_levinenocrp.parquet")',
        f'Path({str(args.test.resolve())!r})',
    )
    exec(config, ns)
    for cell_index in (7, 9, 12, 14):
        exec(nb.cells[cell_index].source, ns)

    table = ns["benchmark_table"].copy()
    test = table.loc[table["cohort"].astype(str).eq("test_benchmark")].copy()
    if len(test) != 5 or set(test["risk_score"]) != set(SUBMITTED["risk_score"]):
        raise AssertionError("canonical notebook did not produce the five expected test rows")
    observed = test.merge(SUBMITTED, on="risk_score", suffixes=("_observed", "_submitted"))
    decimals = {"C_index": 3, "HR_per_1SD": 2, "HR_95CI_low": 2, "HR_95CI_high": 2, "corr_age": 2}
    checks = {}
    for column, places in decimals.items():
        checks[column] = bool(
            observed[f"{column}_observed"].round(places).eq(observed[f"{column}_submitted"]).all()
        )
    if not all(checks.values()):
        raise AssertionError(f"submitted Table 2 rounding mismatch: {checks}")

    table.to_csv(args.output, index=False)
    metadata = {
        "producer": str(NOTEBOOK.relative_to(REPO)),
        "output": str(args.output.resolve()), "output_sha256": sha256(args.output),
        "output_rows": len(table), "test_rows": len(test),
        "train": str(args.train.resolve()), "train_sha256": sha256(args.train),
        "train_rows": len(pd.read_parquet(args.train)),
        "test": str(args.test.resolve()), "test_sha256": sha256(args.test),
        "test_rows_input": len(pd.read_parquet(args.test)),
        "submitted_rounding_checks": checks,
    }
    metadata_path = args.output.with_suffix(".metadata.json")
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n")
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
