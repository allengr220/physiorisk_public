#!/usr/bin/env python3
"""Targeted Sprint 3D regeneration from the canonical notebook-01 rules.

This script imports the cycle loader directly from the retained notebook, caches
and hashes every successful public input, rebuilds the survival populations, and
writes staged cohort diagnostics. It does not fit or modify any model.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from io import BytesIO
from pathlib import Path

import nbformat
import numpy as np
import pandas as pd
import requests


REPO = Path(__file__).resolve().parents[1]
NOTEBOOK = REPO / "notebooks/01_nhanes_extended_dataset_builder.ipynb"

CYCLES = [
    {"label": "1999-2000", "folder": "1999", "suffix": "", "mort": "NHANES_1999_2000_MORT_2019_PUBLIC.dat"},
    {"label": "2001-2002", "folder": "2001", "suffix": "_B", "mort": "NHANES_2001_2002_MORT_2019_PUBLIC.dat"},
    {"label": "2003-2004", "folder": "2003", "suffix": "_C", "mort": "NHANES_2003_2004_MORT_2019_PUBLIC.dat"},
    {"label": "2005-2006", "folder": "2005", "suffix": "_D", "mort": "NHANES_2005_2006_MORT_2019_PUBLIC.dat"},
    {"label": "2007-2008", "folder": "2007", "suffix": "_E", "mort": "NHANES_2007_2008_MORT_2019_PUBLIC.dat"},
    {"label": "2009-2010", "folder": "2009", "suffix": "_F", "mort": "NHANES_2009_2010_MORT_2019_PUBLIC.dat"},
    {"label": "2011-2012", "folder": "2011", "suffix": "_G", "mort": "NHANES_2011_2012_MORT_2019_PUBLIC.dat"},
    {"label": "2013-2014", "folder": "2013", "suffix": "_H", "mort": "NHANES_2013_2014_MORT_2019_PUBLIC.dat"},
    {"label": "2015-2016", "folder": "2015", "suffix": "_I", "mort": "NHANES_2015_2016_MORT_2019_PUBLIC.dat"},
]

EXTENDED_16 = [
    "BMXBMI", "BMXWAIST", "BPXSY1", "BPXDI1", "LBXGH", "LBDHDD",
    "LBXTC", "LBXTR", "LBXSAL", "LBXSCR", "LBXSAPSI", "LBXWBCSI",
    "LBXLYPCT", "LBXGLU", "LBXMCV", "LBXRDW",
]

REQUIRED_BENCHMARK_BIOMARKERS = [
    "LBXSAL", "LBXSCR", "LBXGLU", "LBXLYPCT", "LBXMCV", "LBXRDW",
    "LBXSAPSI", "LBXWBCSI",
]

EXPECTED_SOURCE_BY_CYCLE = {
    "1999-2000": 9965, "2001-2002": 11039, "2003-2004": 10122,
    "2005-2006": 10348, "2007-2008": 10149, "2009-2010": 10537,
    "2011-2012": 9756, "2013-2014": 10175, "2015-2016": 9971,
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def parse_mortality_dat(content: bytes) -> pd.DataFrame:
    rows = []
    for line in content.decode("latin-1", errors="ignore").splitlines():
        if not line.strip():
            continue
        seqn = line[0:5].strip() if len(line) >= 5 else ""
        if not seqn.isdigit():
            continue
        rows.append({
            "SEQN": pd.to_numeric(seqn, errors="coerce"),
            "ELIGSTAT": pd.to_numeric(line[14:15].strip(), errors="coerce"),
            "MORTSTAT": pd.to_numeric(line[15:16].strip(), errors="coerce"),
            "UCOD_LEADING": pd.to_numeric(line[16:19].strip(), errors="coerce"),
            "DIABETES": pd.to_numeric(line[19:20].strip(), errors="coerce"),
            "HYPERTEN": pd.to_numeric(line[20:21].strip(), errors="coerce"),
            "PERMTH_INT": pd.to_numeric(line[42:45].strip(), errors="coerce"),
            "PERMTH_EXM": pd.to_numeric(line[45:48].strip(), errors="coerce"),
        })
    out = pd.DataFrame(rows)
    out["SEQN"] = pd.to_numeric(out["SEQN"], errors="coerce").astype("Int64")
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--staging-dir", type=Path, required=True)
    args = parser.parse_args()
    stage = args.staging_dir.resolve()
    inputs = stage / "inputs"
    outputs = stage / "outputs"
    inputs.mkdir(parents=True, exist_ok=True)
    outputs.mkdir(parents=True, exist_ok=True)

    manifest: list[dict] = []
    session = requests.Session()

    def cached_download(url: str) -> bytes:
        name = url.rsplit("/", 1)[-1]
        folder = url.rstrip("/").split("/")[-3] if "/Nhanes/Public/" in url else "mortality"
        target = inputs / folder / name
        if target.exists():
            content = target.read_bytes()
        else:
            response = session.get(url, timeout=120, allow_redirects=True)
            response.raise_for_status()
            content = response.content
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
        return content

    successful_xpt: dict[str, dict] = {}
    cycle_by_folder = {cycle["folder"]: cycle["label"] for cycle in CYCLES}

    def read_xpt(url: str) -> pd.DataFrame:
        content = cached_download(url)
        df = pd.read_sas(BytesIO(content), format="xport")
        successful_xpt[url] = {
            "input_role": "NHANES public-use component",
            "cycle": cycle_by_folder[url.split("/Public/", 1)[1].split("/", 1)[0]],
            "url": url,
            "filename": url.rsplit("/", 1)[-1],
            "sha256": sha256_bytes(content),
            "bytes": len(content),
            "rows": len(df),
        }
        return df

    nb = nbformat.read(NOTEBOOK, as_version=4)
    namespace = {"pd": pd, "np": np, "requests": requests, "BytesIO": BytesIO}
    # Canonical helper definitions (cell 3) and exact cycle loader (cell 6).
    exec("".join(nb.cells[3].source.splitlines(True)[2:]), namespace)
    namespace["read_xpt"] = read_xpt
    exec(nb.cells[6].source, namespace)
    load_cycle = namespace["load_cycle"]

    cycle_frames = []
    for cycle in CYCLES:
        frame = load_cycle(cycle)
        actual = len(frame)
        expected = EXPECTED_SOURCE_BY_CYCLE[cycle["label"]]
        if actual != expected:
            raise AssertionError(f"{cycle['label']} source N {actual} != {expected}")
        cycle_frames.append(frame)

    source = pd.concat(cycle_frames, ignore_index=True)
    source["cycle_start_year"] = source["CYCLE"].str.split("-").str[0].astype(int)
    if len(source) != 92062 or not source["SEQN"].is_unique:
        raise AssertionError(f"source invariant failed: N={len(source)}, unique={source['SEQN'].is_unique}")

    mort_frames = []
    mort_base = "https://ftp.cdc.gov/pub/Health_Statistics/NCHS/datalinkage/linked_mortality"
    for cycle in CYCLES:
        url = f"{mort_base}/{cycle['mort']}"
        content = cached_download(url)
        mort = parse_mortality_dat(content)
        mort["CYCLE_SRC"] = cycle["label"]
        if len(mort) != EXPECTED_SOURCE_BY_CYCLE[cycle["label"]]:
            raise AssertionError(f"{cycle['label']} mortality row count mismatch")
        mort_frames.append(mort)
        manifest.append({
            "input_role": "NCHS 2019 public linked-mortality file",
            "cycle": cycle["label"], "url": url, "filename": cycle["mort"],
            "sha256": sha256_bytes(content), "bytes": len(content), "rows": len(mort),
        })
    manifest.extend(successful_xpt[url] for url in sorted(successful_xpt))

    mortality = pd.concat(mort_frames, ignore_index=True).drop_duplicates("SEQN")
    merged = source.merge(
        mortality[["SEQN", "ELIGSTAT", "MORTSTAT", "PERMTH_INT", "PERMTH_EXM", "CYCLE_SRC"]],
        on="SEQN", how="left", validate="one_to_one",
    )
    survival = merged.loc[
        merged["ELIGSTAT"].eq(1) & merged["PERMTH_INT"].notna() & merged["MORTSTAT"].notna()
    ].copy()
    if len(survival) != 53255 or int(survival["MORTSTAT"].sum()) != 9104:
        raise AssertionError("mortality-eligible invariant failed")

    included = survival[EXTENDED_16].notna().all(axis=1)
    benchmark = survival.loc[included].copy()
    excluded = survival.loc[~included].copy()
    train = benchmark["cycle_start_year"].le(2010)
    temporal = benchmark["cycle_start_year"].ge(2011)
    invariants = (
        len(benchmark), int(benchmark["MORTSTAT"].sum()), len(excluded),
        int(train.sum()), int(benchmark.loc[train, "MORTSTAT"].sum()),
        int(temporal.sum()), int(benchmark.loc[temporal, "MORTSTAT"].sum()),
    )
    if invariants != (19829, 2936, 33426, 13090, 2520, 6739, 416):
        raise AssertionError(f"cohort invariants failed: {invariants}")

    survival_path = outputs / "nhanes_1999_2016_survival_master.parquet"
    extended_path = outputs / "nhanes_1999_2016_extended_mortality_model_dataset.parquet"
    survival.to_parquet(survival_path, index=False)
    benchmark.to_parquet(extended_path, index=False)

    flow = pd.DataFrame([
        {"flow_stage": "original NHANES source cycles", "count": len(source), "deaths": pd.NA,
         "population_definition": "Nine public-use DEMO cycle files, 1999-2000 through 2015-2016",
         "producer": "notebooks/01_nhanes_extended_dataset_builder.ipynb"},
        {"flow_stage": "mortality eligible", "count": len(survival), "deaths": int(survival.MORTSTAT.sum()),
         "population_definition": "ELIGSTAT == 1 and nonmissing PERMTH_INT/MORTSTAT after one-to-one SEQN linkage",
         "producer": "notebooks/01_nhanes_extended_dataset_builder.ipynb"},
        {"flow_stage": "biomarker-complete benchmark", "count": len(benchmark), "deaths": int(benchmark.MORTSTAT.sum()),
         "population_definition": "Complete case for notebook 01 EXTENDED_16; notebook 02 eight-biomarker check removes no further rows",
         "producer": "notebooks/01_nhanes_extended_dataset_builder.ipynb; notebooks/02_benchmark_dataset_builder.ipynb"},
        {"flow_stage": "training cohort", "count": int(train.sum()), "deaths": int(benchmark.loc[train, "MORTSTAT"].sum()),
         "population_definition": "Biomarker-complete benchmark with cycle_start_year <= 2010",
         "producer": "notebooks/03_demographic_risk_model.ipynb"},
        {"flow_stage": "temporal-validation cohort", "count": int(temporal.sum()), "deaths": int(benchmark.loc[temporal, "MORTSTAT"].sum()),
         "population_definition": "Biomarker-complete benchmark with cycle_start_year >= 2011",
         "producer": "notebooks/03_demographic_risk_model.ipynb"},
    ])
    flow.to_csv(outputs / "cohort_flow.csv", index=False)

    missing_rows = []
    for year, group in survival.groupby("cycle_start_year", sort=True):
        for biomarker in REQUIRED_BENCHMARK_BIOMARKERS:
            n_missing = int(group[biomarker].isna().sum())
            missing_rows.append({
                "cycle_start_year": int(year), "biomarker": biomarker,
                "N_mortality_eligible": len(group), "missing_N": n_missing,
                "missing_percent": 100.0 * n_missing / len(group),
                "denominator_population": "mortality_eligible_before_complete_case_restriction",
            })
    pd.DataFrame(missing_rows).to_csv(outputs / "missingness_by_cycle.csv", index=False)

    characteristics = []
    for label, group in [("benchmark_included", benchmark), ("excluded_before_benchmark", excluded)]:
        characteristics.append({
            "group": label, "population_definition": (
                "Complete for notebook 01 EXTENDED_16" if label == "benchmark_included"
                else "Missing one or more notebook 01 EXTENDED_16 fields"
            ),
            "N": len(group), "age_mean": group.RIDAGEYR.mean(), "age_SD": group.RIDAGEYR.std(ddof=1),
            "female_percent": 100.0 * group.RIAGENDR.eq(2).mean(),
            "deaths_N": int(group.MORTSTAT.sum()), "deaths_percent": 100.0 * group.MORTSTAT.mean(),
            "median_followup_months": group.PERMTH_INT.median(),
        })
    pd.DataFrame(characteristics).to_csv(outputs / "cohort_included_excluded_characteristics.csv", index=False)

    pd.DataFrame(manifest).sort_values(["input_role", "filename"]).to_csv(
        outputs / "s3d_input_manifest.csv", index=False
    )
    output_records = []
    for path in sorted(outputs.iterdir()):
        if path.is_file() and path.name != "s3d_output_manifest.json":
            record = {"path": str(path), "sha256": sha256_file(path), "bytes": path.stat().st_size}
            if path.suffix == ".csv":
                record["rows"] = len(pd.read_csv(path))
            elif path.suffix == ".parquet":
                record["rows"] = len(pd.read_parquet(path))
            output_records.append(record)
    (outputs / "s3d_output_manifest.json").write_text(json.dumps(output_records, indent=2) + "\n")
    print(json.dumps({"source_N": len(source), "survival_N": len(survival), "invariants": invariants,
                      "outputs": output_records}, indent=2))


if __name__ == "__main__":
    main()
