# Pipeline audit

## Method and scope

This static audit inspected code cells, repository paths, documented external hashes, and downstream references. No notebook or scientific analysis was run. “Exists” means committed in this repository unless explicitly marked external. Remote NHANES downloads in notebook 01 are treated as declared source inputs, not committed artifacts.

## Canonical notebook audit

### 01 — `01_nhanes_extended_dataset_builder.ipynb`

- **Inputs:** public NHANES component files and 2019 linked-mortality fixed-width files downloaded at runtime.
- **Outputs:** `nhanes_biomarker_master_verified.parquet`; `nhanes_mortality_2019_verified.parquet`; `nhanes_1999_2016_survival_master.parquet`; `nhanes_1999_2016_extended_mortality_model_dataset.parquet`.
- **Inputs exist:** CONDITIONAL — remote public sources are declared, but not vendored or checked here.
- **Every output has a producer:** YES — this notebook.
- **Outputs present:** NO.
- **Orphaned:** PARTIALLY — its final 1999–2016 filename is not the 1999–2018 filename consumed by notebook 02.
- **Provenance coverage:** YES, with the mismatch recorded.
- **Result:** FAIL.

### 02 — `02_benchmark_dataset_builder.ipynb`

- **Input:** `nhanes_1999_2018_extended_mortality_model_dataset.parquet`.
- **Outputs:** PhenoAge benchmark train/test files, v1-ready train/test files, older benchmark scored train/test files, and `benchmark_physiorisk_v1_metrics.csv`.
- **Inputs exist:** NO in repository; no matching canonical producer.
- **Every output has a producer:** YES — this notebook.
- **Outputs present:** NO.
- **Orphaned:** YES relative to the submitted no-CRP chain: it does not produce `benchmark_levine_no_crp_cohort.parquet`, which notebook 03 requires.
- **Provenance coverage:** YES, with status `PRODUCER MISMATCH`.
- **Result:** FAIL.

### 03 — `03_demographic_risk_model.ipynb`

- **Input:** `benchmark_levine_no_crp_cohort.parquet`.
- **Outputs:** frozen baseline train/test parquets, DemoRisk model pickle, and metadata JSON.
- **Inputs exist:** EXTERNAL ONLY — verified outside Git; absent from the public repository.
- **Every output has a producer:** YES — this notebook.
- **Outputs present:** NO.
- **Orphaned:** NO conceptually; it feeds notebook 04. It is blocked in a clean clone.
- **Provenance coverage:** YES.
- **Result:** FAIL.

### 04 — `04_physiorisk_scoring.ipynb`

- **Inputs:** `physiorisk_v1_frozen_baseline_train_levinenocrp.parquet`; `physiorisk_v1_frozen_baseline_test_levinenocrp.parquet`.
- **Outputs:** scored train/test parquets; evaluation CSV; scoring-stage cohort flow; axis membership; physiology Cox coefficients.
- **Inputs exist:** NO in repository; producer notebook 03 exists but its outputs are uncommitted.
- **Every output has a producer:** YES — this notebook.
- **Outputs present:** scored train/test are EXTERNAL VERIFIED; other exports are absent.
- **Orphaned:** NO; scored files feed notebooks 05–07 and Sprint 2 validation.
- **Provenance coverage:** YES.
- **Result:** FAIL in a clean clone.

### 05 — `05_physiorisk_model_validation.ipynb`

- **Inputs:** scored train/test parquets from notebook 04.
- **Output:** `physiorisk_vs_phenoage_aligned_comparison.csv`.
- **Inputs exist:** EXTERNAL ONLY; both are hash-verified outside Git.
- **Every output has a producer:** YES — this notebook.
- **Output present:** NO; results remain embedded in notebook output/manuscript.
- **Orphaned:** NO; output feeds notebook 06 and submitted Table 2.
- **Provenance coverage:** YES.
- **Result:** FAIL in a clean clone.

### 06 — `06_physiorisk_figures.ipynb`

- **Inputs:** scored test parquet; `test_phenoage_compare_outputs.parquet`; `physiorisk_vs_phenoage_aligned_comparison.csv`.
- **Outputs:** Figure 1 and Figure 2 image exports.
- **Inputs exist:** NO in repository. The scored test file is external verified; the comparison CSV has a producer but is uncommitted; `test_phenoage_compare_outputs.parquet` has no canonical producer.
- **Every output has a producer:** YES at notebook level, although exact file-hash linkage is not asserted.
- **Outputs present:** YES, `figures/Fig1.{png,tiff}` and `figures/Fig2.{png,tiff}`.
- **Orphaned:** NO.
- **Provenance coverage:** YES.
- **Result:** FAIL because required inputs are unavailable.

### 07 — `07_ablation_analysis_optional.ipynb`

- **Inputs:** 1999–2018 extended dataset plus v1/v2/v3 scored train/test parquets.
- **Outputs:** ablation metrics, C-index, HR, and age-correlation CSVs.
- **Inputs exist:** NO; the v1/v2/v3 filenames have no complete canonical producer chain.
- **Every output has a producer:** YES — this notebook.
- **Outputs present:** NO.
- **Orphaned:** YES relative to the main submitted dependency chain; it is explicitly optional and belongs to an older multi-model path.
- **Provenance coverage:** YES.
- **Result:** FAIL.

## Supplemental notebooks

- `07_totalrisk_reconstruction.ipynb` consumes the external verified scored parquets and produces three committed reconstruction tables. It is reproducible only when the external input files are supplied at `data/` or via its environment-variable paths.
- `08_validation_v2.ipynb` and `09_cohort_comparator_sensitivity.ipynb` are non-orphaned display notebooks. Their committed CSV inputs exist. The actual producer is `scripts/run_sprint2_validation.py`, which requires the three external verified parquet inputs.

## Artifact and orphan summary

- **Artifacts without a producer:** `nhanes_1999_2018_extended_mortality_model_dataset.parquet`, `benchmark_levine_no_crp_cohort.parquet`, and `test_phenoage_compare_outputs.parquet`.
- **Produced but uncommitted major inputs/outputs:** all canonical parquets, model pickle/metadata, submitted benchmark CSV, scoring metadata exports, and ablation exports.
- **Orphaned canonical notebooks:** notebook 02 is disconnected from notebook 03; notebook 07 is an optional older branch. Notebook 01 is partially orphaned because of the year-window/filename mismatch.
- **Artifacts lacking documentation provenance after this sprint:** none among the major artifacts identified by static inspection. Documentation coverage does not imply reproducibility.

## PASS/FAIL summary

| Check | Result | Reason |
|---|---|---|
| Canonical names/order | PASS | Seven requested names are present in order; notebook bytes were not edited. |
| Major artifact provenance documented | PASS | Major datasets, figures, tables, validation, and calibration outputs are mapped. |
| Every canonical input has a matching producer | FAIL | Three important inputs have no matching canonical producer. |
| Every required input exists in a clean clone | FAIL | Core parquet/model inputs are not committed. |
| No orphaned canonical notebooks | FAIL | Notebook 02 and optional notebook 07 are disconnected from the submitted chain. |
| End-to-end reproducibility | FAIL | The clean repository cannot execute the canonical chain. |

**Overall: FAIL for end-to-end reproducibility; PASS for static traceability and audit documentation.**
