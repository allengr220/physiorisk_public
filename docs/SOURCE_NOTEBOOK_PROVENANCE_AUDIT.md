# Source notebook provenance audit

## Scope and method

This audit statically inspected all 36 notebooks in `/home/ubuntu2204/cognitive-ledger/longevity/notebooks`. Code cells and notebook documentation were searched for named paths, reads, writes, model serialization, tabular exports, and figure exports. No notebook was executed and no scientific code, coefficients, claims, or paths were changed.

Classifications are relative to the submitted Levine-no-CRP pipeline:

- **PRODUCES** — executable code writes the artifact in the recovered pipeline.
- **CONSUMES** — executable code reads the artifact in the recovered pipeline.
- **MENTIONS ONLY** — prose, a comment, or a path declaration without an applicable read/write.
- **OBSOLETE / HISTORICAL** — an occurrence belongs to an older or different scientific branch, even if that code reads or writes the named artifact.
- **UNCLEAR** — the occurrence cannot establish the claimed lineage.

## Finding

The submitted no-CRP lineage is recoverable and unambiguous through the benchmark-comparison stage:

1. `nhanes_extended_dataset_builderV3.ipynb`
2. `benchmark_levine_no_crp_cohort_builder.ipynb`
3. `baseline_risk_builder_v1_split_aware_export_levinenocrp.ipynb`
4. `physiorisk_canonical_frozen_baseline_notebook_levinenocrp.ipynb`
5. `physiorisk_vs_phenoage_aligned_minimal_comparison_frozen.ipynb`
6. `physiorisk_vs_phenoage_figures.ipynb`

Sprint 3C repaired the public copy after this archive investigation. Public notebooks 01, 03, 04, and 06 remain byte-identical to their archive sources. Public notebook 02 is now byte-identical to the correct no-CRP builder. Public notebook 05 now preserves the more complete former top-level public copy, which adds the verified row-level comparator export absent from the archive copy inspected in Sprint 3B.

## Exact identity comparison

| Public notebook | Archive notebook | SHA256 | Finding |
|---|---|---|---|
| `01_nhanes_extended_dataset_builder.ipynb` | `nhanes_extended_dataset_builderV3.ipynb` | `1661c2d717c515868d84778874a61e137315e3c5c8f83f367af8f2a7b5812fc9` | Exact match; correct upstream builder |
| `02_benchmark_dataset_builder.ipynb` | `benchmark_levine_no_crp_cohort_builder.ipynb` | `612a52cb8d585bc48a5629cf35c26d469d378f6cf9b0e15b6251f364b978c103` | Sprint 3C exact replacement; correct no-CRP branch |
| `03_demographic_risk_model.ipynb` | `baseline_risk_builder_v1_split_aware_export_levinenocrp.ipynb` | `7d19c67409462505d98671a6c1ebecbfebb29e1bd25d9e38b2e003f293545944` | Exact match; correct |
| `04_physiorisk_scoring.ipynb` | `physiorisk_canonical_frozen_baseline_notebook_levinenocrp.ipynb` | `61100d7f1a9adc130a7781ae0012cc3d88fab93f1e48729085442781f7308a59` | Exact match; correct |
| `05_physiorisk_model_validation.ipynb` | More complete former top-level `physiorisk_vs_phenoage_aligned_minimal_comparison_frozen.ipynb` | `fa057c1f42304a05871d3f236b79c895ea596afcc72351d250eb65144a69e62c` | Supersedes archive copy by adding verified row-level comparator export |
| `06_physiorisk_figures.ipynb` | `physiorisk_vs_phenoage_figures.ipynb` | `2760b3307abb3f6dea86b8c4b5ab4391f1b9ac9094948c0dcfc57249926572d2` | Exact match; correct, with one unresolved row-level comparator input |

The correct archive source for public notebook 02 is `benchmark_levine_no_crp_cohort_builder.ipynb`, SHA256 `612a52cb8d585bc48a5629cf35c26d469d378f6cf9b0e15b6251f364b978c103`; that source is now installed.

## Artifact occurrence table: recovered no-CRP chain

| Artifact | Notebook occurrence | Classification | Evidence/role |
|---|---|---|---|
| `nhanes_biomarker_master_verified.parquet` | `nhanes_extended_dataset_builderV3.ipynb` | PRODUCES | Writes the all-cycle harmonized biomarker intermediate. |
| `nhanes_mortality_2019_verified.parquet` | `nhanes_extended_dataset_builderV3.ipynb` | PRODUCES | Writes the verified mortality-linkage intermediate. |
| `nhanes_1999_2016_survival_master.parquet` | `nhanes_extended_dataset_builderV3.ipynb` | PRODUCES | Writes the complete mortality-linked survival master. |
| `nhanes_1999_2016_survival_master.parquet` | `baseline_risk_builder_v1_frozen.ipynb` | OBSOLETE / HISTORICAL | Reads it for a full-cohort reference/inspection fit explicitly marked unsuitable for temporal validation claims. |
| `nhanes_1999_2016_extended_mortality_model_dataset.parquet` | `nhanes_extended_dataset_builderV3.ipynb` | PRODUCES | Exact final path written as `EXTENDED_MODEL_PATH`; survival window is explicitly frozen to 1999–2016. |
| Same 1999–2016 extended dataset | `benchmark_levine_no_crp_cohort_builder.ipynb` | CONSUMES | Exact `MASTER_PATH`; constructs the submitted no-CRP cohort. |
| Same 1999–2016 extended dataset | `baseline_risk_builder_v1_split_aware_export.ipynb` | OBSOLETE / HISTORICAL | Generic non-benchmark baseline branch. |
| Same 1999–2016 extended dataset | `nhanes_physiorisk_3axis_v1_working.ipynb` | OBSOLETE / HISTORICAL | Older three-axis publication-export branch. |
| Same 1999–2016 extended dataset | `physiorisk_validation_comparison.ipynb` | OBSOLETE / HISTORICAL | Reads raw data for a comparator in the non-no-CRP scored branch. |
| Same 1999–2016 extended dataset | `nhanes_extended_dataset_builderV3.ipynb` markdown | MENTIONS ONLY | Frozen-spec documentation duplicates the executable path/role. |
| `benchmark_levine_no_crp_cohort.parquet` | `benchmark_levine_no_crp_cohort_builder.ipynb` | PRODUCES | Drops incomplete required fields, selects 14 columns, deduplicates `SEQN`, and writes the expected N=19,829/deaths=2,936 cohort. |
| Same no-CRP cohort | `baseline_risk_builder_v1_split_aware_export_levinenocrp.ipynb` | CONSUMES | Exact `COHORT_PATH`; temporal split and frozen DemoRisk fitting. |
| Same no-CRP cohort | `benchmark_levine_no_crp_cohort_builder.ipynb` markdown | MENTIONS ONLY | Declares output and downstream contract. |
| `physiorisk_v1_frozen_baseline_train_levinenocrp.parquet` | `baseline_risk_builder_v1_split_aware_export_levinenocrp.ipynb` | PRODUCES | Training split with fitted `BaselineRisk`; written in cell 20. |
| Same baseline train parquet | `physiorisk_canonical_frozen_baseline_notebook_levinenocrp.ipynb` | CONSUMES | Exact `TRAIN_PATH`; no baseline refit downstream. |
| `physiorisk_v1_frozen_baseline_test_levinenocrp.parquet` | `baseline_risk_builder_v1_split_aware_export_levinenocrp.ipynb` | PRODUCES | Temporal test split scored with frozen training model. |
| Same baseline test parquet | `physiorisk_canonical_frozen_baseline_notebook_levinenocrp.ipynb` | CONSUMES | Exact `TEST_PATH`. |
| `baseline_risk_v1_temporal_fit_levinenocrp.pkl` | `baseline_risk_builder_v1_split_aware_export_levinenocrp.ipynb` | PRODUCES | `joblib.dump` of the training-fitted DemoRisk Cox model. No downstream notebook deserializes it. |
| `baseline_risk_v1_temporal_metadata_levinenocrp.json` | `baseline_risk_builder_v1_split_aware_export_levinenocrp.ipynb` | PRODUCES | Records cohort path, split, formula, penalty, design columns, N, and event counts. |
| `physiorisk_2axis_v1_train_scored_from_frozen_baseline_levinenocrp.parquet` | `physiorisk_canonical_frozen_baseline_notebook_levinenocrp.ipynb` | PRODUCES | Exact output written from the two-axis scoring workflow. |
| Same scored train parquet | `physiorisk_vs_phenoage_aligned_minimal_comparison_frozen.ipynb` | CONSUMES | Exact `TRAIN_PATH`; used for training-only comparator preprocessing. |
| `physiorisk_2axis_v1_test_scored_from_frozen_baseline_levinenocrp.parquet` | `physiorisk_canonical_frozen_baseline_notebook_levinenocrp.ipynb` | PRODUCES | Exact output written from the two-axis scoring workflow. |
| Same scored test parquet | `physiorisk_vs_phenoage_aligned_minimal_comparison_frozen.ipynb` | CONSUMES | Exact `TEST_PATH`; source for submitted temporal comparison. |
| Same scored test parquet | `physiorisk_vs_phenoage_figures.ipynb` | CONSUMES | Exact `TEST_SCORED_PATH`; source for manuscript figures. |
| `physiorisk_2axis_v1_eval_from_frozen_baseline_levinenocrp.csv` | `physiorisk_canonical_frozen_baseline_notebook_levinenocrp.ipynb` | PRODUCES | Evaluation summary, conditional on `eval_all`. |
| `physiorisk_2axis_v1_cohort_flow_levinenocrp.csv` | Same scoring notebook | PRODUCES | Train/test counts and events at scoring stage. |
| `physiorisk_2axis_v1_axis_membership.csv` | Same scoring notebook | PRODUCES | Axis membership and sign convention. |
| `physiorisk_2axis_v1_physio_cox_coefficients.csv` | Same scoring notebook | PRODUCES | Physiology Cox summary. |
| `physiorisk_vs_phenoage_aligned_comparison.csv` | `physiorisk_vs_phenoage_aligned_minimal_comparison_frozen.ipynb` | PRODUCES | Exact submitted benchmark-comparison table export. |
| Same comparison CSV | `physiorisk_vs_phenoage_figures.ipynb` | CONSUMES | Exact `BENCHMARK_TABLE_PATH`; drives Figure 2. |
| `test_phenoage_compare_outputs.parquet` | Public `05_physiorisk_model_validation.ipynb` | PRODUCES | The preserved top-level public version explicitly writes `SEQN`, `PhenoAge_noCRP_proxy`, and `PhenoAgeAccel`. |
| Same row-level comparator parquet | `physiorisk_vs_phenoage_figures.ipynb` | CONSUMES | Used when `PhenoAgeAccel` is absent from the scored test file. |
| `Fig1.png`, `Fig1.tiff`, `Fig1.pdf` | `physiorisk_vs_phenoage_figures.ipynb` | PRODUCES | Kaplan–Meier panels by PhysioRisk and PhenoAge NCP acceleration quartiles. |
| `Fig2.png`, `Fig2.tiff`, `Fig2.pdf` | Same figure notebook | PRODUCES | C-index, HR/SD, and age-correlation comparison panels. |
| Figure captions | Same figure notebook | PRODUCES | Caption strings are emitted in the final cell; manuscript assembly is outside the notebook. |
| Manuscript Table 1 standalone source | Archive as a whole | UNCLEAR | No exact standalone Table 1 export was found; it is embedded in the manuscript. |
| Manuscript Table 2 | Comparison notebook and `physiorisk_vs_phenoage_aligned_comparison.csv` | PRODUCES | The notebook output matches the submitted benchmark table lineage documented in Sprint 1. |

## Artifact occurrence table: 1999–2018 and other historical branches

These occurrences explain why the wrong notebook 02 looked superficially plausible. They are real workflows, but they do not produce the submitted no-CRP chain.

| Artifact/family | Every archive notebook occurrence | Classification | Reason |
|---|---|---|---|
| `nhanes_1999_2018_extended_mortality_model_dataset.parquet` | `nhanes_extended_dataset_builder.ipynb`; `nhanes_extended_dataset_builderV2.ipynb` | OBSOLETE / HISTORICAL | Both write a 1999–2018-named dataset from earlier workflows; V3 supersedes this for mortality-linked 1999–2016 analysis. |
| Same 1999–2018 extended dataset | `benchmark_dataset_builder_PRscore.ipynb`; `nhanes_full_research_dataset_builder.ipynb`; `nhanes_physiorisk_3axis_crp_interactions_v3.ipynb`; `nhanes_physiorisk_3axis_crp_linear_v2.ipynb`; `nhanes_physiorisk_3axis_crp_spline_v4.ipynb`; `nhanes_physiorisk_3axis_v1_frozen.ipynb`; `nhanes_physiorisk_ablation_v1.ipynb` | OBSOLETE / HISTORICAL | Consumers belong to CRP-complete, three-axis, full-research, or ablation branches rather than the submitted two-axis no-CRP chain. |
| `nhanes_1999_2018_extended_mortality_model_dataset_complete.parquet` | `nhanes_extended_dataset_builder.ipynb` | OBSOLETE / HISTORICAL | Earlier builder writes the mortality-complete variant. |
| Same “complete” dataset | `NHANES_Survival_Derived_Biological_Age.ipynb`; `nhanes_extended_biomarker_clock.ipynb`; `nhanes_physiorisk_temporal_validation.ipynb` | OBSOLETE / HISTORICAL | Reads support earlier clock/validation work. |
| Same “complete” dataset | `NHANES_Resilient_Aging_Phenotypes.ipynb` | MENTIONS ONLY | Read is commented out. |
| `nhanes_1999_2018_full_research_dataset.parquet` | `nhanes_full_research_dataset_builder.ipynb` | OBSOLETE / HISTORICAL | Writes a broader merged research dataset. |
| Same full-research dataset | `NHANES_survival_based_physiorisk_benchmark.ipynb`; `PhysioRisk_FINAL_pipeline.ipynb`; `physiorisk_frozen_model_export.ipynb` | OBSOLETE / HISTORICAL | Reads feed older high-dimensional/frozen-export branches. |
| `physiorisk_phenoage_benchmark_{train,test}.parquet`; `_v1ready` variants; `benchmark_physiorisk_v1_{train,test}_scored.parquet`; `benchmark_physiorisk_v1_metrics.csv` | `benchmark_dataset_builder_PRscore.ipynb` | OBSOLETE / HISTORICAL | Produces the CRP-required, three-axis PR-score branch removed from public notebook 02 in Sprint 3C. |
| Those PR-score benchmark artifacts | `physiorisk_vs_phenoage_minimal_comparison.ipynb` | OBSOLETE / HISTORICAL | Consumes the older benchmark branch and writes merged/result artifacts. |
| `physiorisk_vs_phenoage_results.csv` and merged benchmark parquets | `physiorisk_vs_phenoage_minimal_comparison.ipynb` | OBSOLETE / HISTORICAL | Earlier comparison output, not the aligned frozen no-CRP comparison CSV. |
| Generic frozen baseline train/test/model/metadata without `_levinenocrp` | `baseline_risk_builder_v1_split_aware_export.ipynb`; `physiorisk_canonical_frozen_baseline_notebook.ipynb` | OBSOLETE / HISTORICAL | Valid generic 1999–2016 branch, but not the cohort-aligned submitted artifacts. |
| `physiorisk_2axis_v1_{train,test}_scored_from_frozen_baseline.parquet` without `_levinenocrp` | `physiorisk_canonical_frozen_baseline_notebook.ipynb`; `physiorisk_validation_comparison.ipynb` | OBSOLETE / HISTORICAL | Earlier non-aligned scored branch. |
| `physiorisk_v1_train.parquet`, `physiorisk_v1_test.parquet`, v2/v3 scored files, and ablation CSVs | `nhanes_physiorisk_3axis_v1_frozen.ipynb`; CRP v2/v3 notebooks; `nhanes_physiorisk_ablation_v1.ipynb`; `physiorisk_calibration_comparison_notebook.ipynb` | OBSOLETE / HISTORICAL | Three-axis/CRP ablation and calibration lineage, not the submitted two-axis no-CRP model. |
| `nhanes_physiorisk_{train,test}_scored.parquet` and related coefficient/validation outputs | `NHANES_survival_based_physiorisk_benchmark.ipynb`; `physiorisk_LOO_diagnostics.ipynb`; `physiorisk_internal_validation_suite.ipynb` | OBSOLETE / HISTORICAL | Earlier full-research PhysioRisk branch. |
| Survival/biological-age train/test parquets and performance CSVs | `NHANES_Survival_Derived_Biological_Age.ipynb`; `NHANES_Resilient_Aging_Phenotypes.ipynb`; biological-age clock notebooks | OBSOLETE / HISTORICAL | Separate clock/phenotype research, not a producer or consumer in the submitted chain. |

## Candidate notebook decisions

### Public notebook 02

**The prior copy was wrong for the submitted pipeline; Sprint 3C replaced it unambiguously.**

- Prior public copy: `benchmark_dataset_builder_PRscore.ipynb`.
- It reads `nhanes_1999_2018_extended_mortality_model_dataset.parquet`.
- It requires the full Levine panel including positive CRP, builds a stricter 16-biomarker/three-axis subset, and writes differently named PR-score artifacts.
- It never writes `benchmark_levine_no_crp_cohort.parquet`.
- Current/correct source: `benchmark_levine_no_crp_cohort_builder.ipynb`.
- The correct source reads the exact output of public notebook 01 and writes the exact input of public notebook 03.

### Public notebook 01

**Correct for the submitted pipeline, unambiguously.**

- `nhanes_extended_dataset_builder.ipynb` is an older 1999–2018/“complete” builder.
- `nhanes_extended_dataset_builderV2.ipynb` also writes a 1999–2018-named output and does not enforce the final V3 survival-window contract.
- `nhanes_full_research_dataset_builder.ipynb` consumes an older 1999–2018 dataset to build a broader research dataset; it is not the upstream source.
- `nhanes_extended_dataset_builderV3.ipynb` writes `nhanes_1999_2016_extended_mortality_model_dataset.parquet`, exactly matching the true no-CRP builder's `MASTER_PATH`.
- Public notebook 01 is byte-identical to V3.

## Producer/consumer map

```text
nhanes_extended_dataset_builderV3.ipynb
  PRODUCES nhanes_1999_2016_extended_mortality_model_dataset.parquet
      |
      v
benchmark_levine_no_crp_cohort_builder.ipynb
  PRODUCES benchmark_levine_no_crp_cohort.parquet
      |
      v
baseline_risk_builder_v1_split_aware_export_levinenocrp.ipynb
  PRODUCES frozen baseline train/test + model pickle + metadata JSON
      |
      v
physiorisk_canonical_frozen_baseline_notebook_levinenocrp.ipynb
  PRODUCES scored train/test + evaluation/axis/coefficient CSVs
      |
      v
physiorisk_vs_phenoage_aligned_minimal_comparison_frozen.ipynb
  PRODUCES physiorisk_vs_phenoage_aligned_comparison.csv
      |
      v
physiorisk_vs_phenoage_figures.ipynb
  PRODUCES Fig1/Fig2 PNG, TIFF, and PDF
  CONSUMES notebook 05's test_phenoage_compare_outputs.parquet if
  row-level PhenoAgeAccel is absent from the scored test file
```

## Public repository mismatch list

1. **Resolved:** notebook 02 is now the recovered no-CRP builder and the 01 → 02 → 03 contract is direct.
2. **Resolved:** notebook 05 now explicitly produces `test_phenoage_compare_outputs.parquet`.
3. **Remaining external limitation:** the small exact DemoRisk model/metadata and scoring metadata CSVs are defined by producers but are absent from Git and the searched WSL archive.
4. **Remaining external limitation:** large canonical datasets stay outside Git. Three are locally hash-verified under `/home/ubuntu2204/longevity/data/physiorisk/data`.
5. **Remaining provenance gap:** no exact standalone producer/export for manuscript Table 1 was identified.

## Recommended corrected canonical sequence

| Public number/name | Archive source | Action |
|---|---|---|
| `01_nhanes_extended_dataset_builder.ipynb` | `nhanes_extended_dataset_builderV3.ipynb` | Keep unchanged. |
| `02_benchmark_dataset_builder.ipynb` | `benchmark_levine_no_crp_cohort_builder.ipynb` | Completed in Sprint 3C; archive bytes preserved exactly. |
| `03_demographic_risk_model.ipynb` | `baseline_risk_builder_v1_split_aware_export_levinenocrp.ipynb` | Keep unchanged. |
| `04_physiorisk_scoring.ipynb` | `physiorisk_canonical_frozen_baseline_notebook_levinenocrp.ipynb` | Keep unchanged. |
| `05_physiorisk_model_validation.ipynb` | More complete former top-level validation copy | Preserved in Sprint 3C; row-level comparator export verified. |
| `06_physiorisk_figures.ipynb` | `physiorisk_vs_phenoage_figures.ipynb` | Keep unchanged; its row-level comparator input now has a verified producer. |

`07_ablation_analysis_optional.ipynb` is not part of this direct dependency chain. It belongs to an older 1999–2018 v1/v2/v3 branch and should remain clearly labeled optional/historical unless a submitted-two-axis ablation is later created as new analysis. Notebooks 07–09 from the post-review work remain supplemental and should not be inserted between recovered canonical stages 01–06.

## Artifacts missing from the public repo

### Found locally outside Git

- `benchmark_levine_no_crp_cohort.parquet`
- `physiorisk_2axis_v1_train_scored_from_frozen_baseline_levinenocrp.parquet`
- `physiorisk_2axis_v1_test_scored_from_frozen_baseline_levinenocrp.parquet`

These are large/person-level derived data and should not be committed automatically. Continue to document hashes, row/event counts, access conditions, and a public acquisition/rebuild route.

### Not found in the public repo or searched archive filesystem

- `nhanes_1999_2016_extended_mortality_model_dataset.parquet`
- `physiorisk_v1_frozen_baseline_train_levinenocrp.parquet`
- `physiorisk_v1_frozen_baseline_test_levinenocrp.parquet`
- `baseline_risk_v1_temporal_fit_levinenocrp.pkl`
- `baseline_risk_v1_temporal_metadata_levinenocrp.json`
- `physiorisk_2axis_v1_eval_from_frozen_baseline_levinenocrp.csv`
- `physiorisk_2axis_v1_cohort_flow_levinenocrp.csv`
- `physiorisk_2axis_v1_axis_membership.csv`
- `physiorisk_2axis_v1_physio_cox_coefficients.csv`
- `physiorisk_vs_phenoage_aligned_comparison.csv`
- `test_phenoage_compare_outputs.parquet` (producer verified; expected in MyDrive)
- Figure PDF exports (`Fig1.pdf`, `Fig2.pdf`); PNG/TIFF exports are committed.
- A standalone source/output for manuscript Table 1.

## Artifacts that should remain excluded from Git

- Raw downloaded NHANES component files and linked-mortality source files: public upstream data, large, and governed by their source distribution terms.
- Participant-level intermediate and analytic parquets: large and potentially disclosure-sensitive despite public-use origins; publish via an explicit data policy or reproducible build route rather than silently adding them.
- Private Google Drive paths and directory layouts: environment-specific metadata, not portable public artifacts.
- Older 1999–2018, full-research, biological-age, three-axis, CRP, v2/v3, and exploratory scored artifacts: historical branches that would confuse the submitted no-CRP lineage.
- Pickles from unrelated historical models: unsafe/non-portable serialization and not part of the recovered submitted chain.

The exact frozen no-CRP DemoRisk pickle and metadata are not “historical”; if recovered, the metadata JSON is a strong candidate for version control after privacy inspection. The pickle should be evaluated for portability and safe distribution, with its hash and reconstruction notebook documented regardless of whether it is committed.
