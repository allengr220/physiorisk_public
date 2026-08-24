# Pipeline audit

## Scope and classification

This static Sprint 3C audit inspected canonical notebook code cells, exact filenames, repository artifacts, the external-artifact manifest, and source-notebook hashes. No notebook was executed.

- **PASS** — role and producer/consumer contract are complete using committed artifacts or public-source regeneration.
- **PASS_WITH_EXTERNAL_ARTIFACTS** — producer graph is complete, but one or more expected large artifacts reside outside Git.
- **PARTIAL** — a documented non-core output or supporting branch remains incomplete.
- **FAIL** — a required direct-pipeline input or major output has no producer or storage/provisioning record.

## Canonical notebooks

### 01 — `01_nhanes_extended_dataset_builder.ipynb`

- **Role:** harmonize public NHANES inputs and linked mortality, then build the 1999–2016 analytic dataset.
- **Inputs:** public NHANES cycle/component files and public linked-mortality files.
- **Major output:** `nhanes_1999_2016_extended_mortality_model_dataset.parquet`.
- **Input disposition:** public-source inputs are declared; raw files are not committed by design.
- **Output producer documented:** YES.
- **Downstream consumer:** notebook 02.
- **Result:** PASS.

### 02 — `02_benchmark_dataset_builder.ipynb`

- **Role:** define the aligned Levine-no-CRP benchmark cohort; no model fitting.
- **Input:** notebook 01's `nhanes_1999_2016_extended_mortality_model_dataset.parquet`.
- **Output:** `benchmark_levine_no_crp_cohort.parquet`.
- **Input disposition:** regenerable from public sources via notebook 01.
- **Output producer documented:** YES; explicit `to_parquet`.
- **Downstream consumer:** notebook 03 and Sprint 2 validation.
- **Correct no-CRP producer:** YES. The former PR-score/CRP-complete notebook was replaced byte-for-byte with the recovered archive source.
- **Result:** PASS_WITH_EXTERNAL_ARTIFACTS because the produced participant-level parquet is not committed.

### 03 — `03_demographic_risk_model.ipynb`

- **Role:** make the temporal split, fit training-only DemoRisk (legacy identifier `BaselineRisk`), apply it frozen to test, and serialize model metadata.
- **Input:** `benchmark_levine_no_crp_cohort.parquet`.
- **Outputs:** frozen baseline train/test parquets, DemoRisk pickle, and metadata JSON.
- **Input disposition:** producer documented in notebook 02; external hash-verified copy exists.
- **Output producers documented:** YES.
- **Output storage:** expected in Google Drive/MyDrive; absent from Git/WSL inventory.
- **Result:** PASS_WITH_EXTERNAL_ARTIFACTS.

### 04 — `04_physiorisk_scoring.ipynb`

- **Role:** consume frozen DemoRisk-scored splits, fit/apply the locked two-axis physiology workflow, and export scored train/test cohorts.
- **Inputs:** frozen baseline train/test parquets from notebook 03.
- **Major outputs:** `physiorisk_2axis_v1_{train,test}_scored_from_frozen_baseline_levinenocrp.parquet` plus evaluation, cohort-flow, axis-membership, and coefficient CSVs.
- **Inputs disposition:** documented upstream producers and external MyDrive entries.
- **Scored-parquet producer:** YES.
- **Output storage:** both scored parquets have external hash-verified WSL copies and expected MyDrive paths; not committed by design.
- **Result:** PASS_WITH_EXTERNAL_ARTIFACTS.

### 05 — `05_physiorisk_model_validation.ipynb`

- **Role:** construct PhenoAge NCP and PhenoAge NCP acceleration on the aligned cohort and produce the submitted comparison outputs.
- **Inputs:** scored train/test parquets from notebook 04.
- **Outputs:** `physiorisk_vs_phenoage_aligned_comparison.csv` and `test_phenoage_compare_outputs.parquet`.
- **Inputs disposition:** producer documented; external hash-verified scored files exist.
- **Aggregate benchmark producer:** YES.
- **Row-level comparator producer:** YES. An explicit `test_compare_export.to_parquet(...)` cell writes `test_phenoage_compare_outputs.parquet`.
- **Output storage:** expected in Google Drive/MyDrive; not committed.
- **Result:** PASS_WITH_EXTERNAL_ARTIFACTS.

### 06 — `06_physiorisk_figures.ipynb`

- **Role:** generate manuscript Figures 1 and 2 without refitting upstream models.
- **Inputs:** scored test parquet from notebook 04 and both notebook 05 outputs.
- **Outputs:** `Fig1` and `Fig2` in PNG/TIFF/PDF formats.
- **Input disposition:** all have documented upstream producers and external manifest entries.
- **Outputs present:** PNG/TIFF are committed; PDF exports remain external.
- **Result:** PASS_WITH_EXTERNAL_ARTIFACTS.

### 07 — `07_ablation_analysis_optional.ipynb`

- **Role:** optional historical v1/v2/v3 ablation/supporting analysis.
- **Inputs/outputs:** older 1999–2018 and multi-model artifacts listed in the manifest/source audit.
- **Direct manuscript-chain requirement:** NO.
- **Result:** PARTIAL. Producer code is present, but its external inputs/outputs are not locally verified and it does not test the submitted two-axis model directly.

## Supplemental post-review notebooks

- `07_totalrisk_reconstruction.ipynb` consumes the external hash-verified scored parquets and produced three committed reconstruction tables.
- `08_validation_v2.ipynb` and `09_cohort_comparator_sensitivity.ipynb` display committed tables produced by `scripts/run_sprint2_validation.py`.
- The script's three main parquet inputs have producer-verified manifest entries and external hash-verified WSL copies.

## Audit questions

| Question | Result | Evidence |
|---|---|---|
| Does every canonical notebook have an assigned role? | PASS | Roles are specified above and in `NOTEBOOK_ORDER.md`. |
| Does every direct-pipeline input have a committed artifact, external manifest entry, or upstream producer? | PASS | Every notebook 01–06 input is covered by public-source regeneration or `ARTIFACT_MANIFEST.tsv`. |
| Does every major direct-pipeline output have a documented producer? | PASS | Notebook 01–06 outputs are mapped in `ARTIFACT_PROVENANCE.md`. |
| Is notebook 02 the correct no-CRP cohort producer? | PASS | It writes the exact cohort consumed by notebook 03; archive/source hash verified. |
| Is notebook 04 the scored-parquet producer? | PASS | Both exact output filenames are written explicitly. |
| Is notebook 05 the benchmark/PhenoAge comparison producer? | PASS | Aggregate and row-level exports are explicit. |
| Is `test_phenoage_compare_outputs.parquet` orphaned? | PASS | No; notebook 05 is producer-verified. |
| Are large external datasets mistaken for producer failures? | PASS | They are labeled external Google Drive/MyDrive artifacts rather than orphans. |
| Is the optional ablation branch fully provisioned and submitted-model aligned? | PARTIAL | Historical inputs/outputs are external and lineage differs from the submitted two-axis model. |
| Is standalone manuscript Table 1 provenance complete? | PARTIAL | Embedded table exists; exact standalone producer/export remains unidentified. |

## Overall result

**PASS_WITH_EXTERNAL_ARTIFACTS for the minimum direct manuscript pipeline (notebooks 01–06).**

The former notebook 01/02 mismatch and the no-CRP cohort producer gap are fixed. The row-level comparator parquet is producer-verified. Remaining limitations are expected external-data availability, environment-specific MyDrive paths, one standalone manuscript-table provenance gap, and a historical optional ablation branch. A clean clone is not self-contained, but the pipeline is internally coherent and auditable.
