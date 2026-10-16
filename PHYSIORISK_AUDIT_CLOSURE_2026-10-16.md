# PhysioRisk audit closure — 2026-10-16

## Status

- Scientific audit: **CLOSED**.
- Research Square v3: **SUBMITTED, AWAITING POSTING**.
- Biogerontology resubmission: **DEFERRED PENDING RS V3 POSTING**.

## Canonical scientific state

The corrected, frozen reader-facing files are:

- `submission/biogerontology/PhysioRisk_Biogerontology_Manuscript_corrected_complete_2026-10-16.docx` and its rendered PDF.
- `submission/biogerontology/PhysioRisk_Biogerontology_Supplementary_Material_corrected_preserved_2026-10-16.docx` and its rendered PDF.

The numerical authority is `outputs/physiorisk_v2_validation/`, including the primary-validation metrics, paired C-index bootstrap, fixed-horizon calibration, calibration plot data, proportional-hazards diagnostics, time-interaction diagnostics, and censoring-robust discrimination artifacts. Supporting corrected refit and comparator outputs are retained under `outputs/physiorisk_2axis_v2_refit/` and `outputs/phenoage_ncp_v2/`.

The document reconstruction records are `MANUSCRIPT_REPAIR_RECONCILIATION_2026-10-16.md` and `SUPPLEMENT_PRESERVATION_RECONCILIATION_2026-10-16.md`.

Repository state at closure preparation:

- Branch: `fix/creatinine-unit-harmonization-v2`
- HEAD: `c3de81f45f70df32a245948d31f690d6b30aae91`
- Working tree: no tracked scientific file is modified by this closure work. Existing untracked reconstruction deliverables remain outside this documentation-only closeout.

## Defects identified and corrected

Two substantive implementation defects were corrected:

1. Inconsistent cross-cycle creatinine-unit handling.
2. Incorrect implementation of the PhenoAge no-CRP comparator.

The corrected pipeline harmonized the affected laboratory inputs, rebuilt the PhenoAge no-CRP comparator with its specified units and linear glucose term, refit dependent quantities, and reran affected validation analyses.

## What changed

Frozen outputs were used to update the affected PhysioRisk quantities where dependent on the repaired input, the PhenoAge NCP values, paired discrimination contrasts, fixed-horizon calibration, proportional-hazards diagnostics, censoring-robust discrimination, Figure 2, and affected supplementary tables. The corrected reader-facing supplement retains the approved table structure and excludes historical S9/S10 material.

## What did not change

- Cohort membership.
- Development and temporal-validation split.
- Main scientific interpretation.
- Model conceptual structure.

## Known scientific limitation retained

The model-development history does not establish that every decision leading to the final two-axis specification was made without reference to later-cycle outcomes. Therefore, the temporal cohort is not a pristine never-examined holdout. This is a scientific limitation, not an implementation defect.

## Superseded material

Historical submission files, archived reader-facing material, and pre-repair result tables must not be treated as current scientific results. This includes historical calibration, discrimination, proportional-hazards, time-interaction, and comparison outputs under `tables/` and archived submission material. The current scientific authority is the version-qualified validation output set in `outputs/physiorisk_v2_validation/` together with the frozen corrected manuscript and preserved supplement named above.

Historical S9 remains repository provenance only and is not part of the corrected reader-facing supplement.

## Cohort provenance verdict

The five reported cohort counts and death counts are algorithmically derived from the public source-cycle NHANES files and public linked mortality records:

| Stage | Rule | N | Deaths |
|---|---|---:|---:|
| Source cycles | Concatenate the nine 1999–2016 continuous NHANES cycles | 92,062 | — |
| Mortality eligible | `ELIGSTAT == 1` with nonmissing `PERMTH_INT` and `MORTSTAT` after a one-to-one `SEQN` linkage | 53,255 | 9,104 |
| Biomarker-complete benchmark | Nonmissing `EXTENDED_16` fields | 19,829 | 2,936 |
| Development | Benchmark participants with cycle start year through 2010 | 13,090 | 2,520 |
| Temporal validation | Benchmark participants with cycle start year from 2011 | 6,739 | 416 |

| Stage | Source files | Exact construction | Computed or hard-coded | Downstream result artifact |
|---|---|---|---|---|
| Source cycles | The nine public NHANES DEMO, examination, and laboratory cycle frames assembled by notebook 01 | Concatenate cycle frames after `SEQN` uniqueness checks | Computed; 92,062 is an expected-value assertion | `nhanes_biomarker_master_verified.parquet` and `cohort_flow.csv` |
| Mortality eligible | Participant master plus matching NCHS 2019 public Linked Mortality Files | Left one-to-one merge on numeric `SEQN`; retain `ELIGSTAT == 1` with nonmissing `PERMTH_INT` and `MORTSTAT` | Computed; 53,255/9,104 are expected-value assertions | `nhanes_1999_2016_survival_master.parquet` and `cohort_flow.csv` |
| Biomarker-complete benchmark | Survival master | Require nonmissing values for every `EXTENDED_16` variable | Computed; 19,829/2,936 are expected-value assertions | `nhanes_1999_2016_extended_mortality_model_dataset.parquet`, `benchmark_levine_no_crp_cohort.parquet`, and `cohort_flow.csv` |
| Development | Benchmark cohort | `cycle_start_year <= 2010` | Computed; 13,090/2,520 are expected-value assertions | `development_cohort.parquet` and `cohort_flow.csv` |
| Temporal validation | Benchmark cohort | `cycle_start_year >= 2011` | Computed; 6,739/416 are expected-value assertions | `validation_cohort.parquet` and `cohort_flow.csv` |

Notebook 01 implements the construction rules. `scripts/run_s3d_cohort_regeneration.py` independently reuses its cycle loader, reconstructs the cohorts from public inputs, and asserts these totals. The totals also occur elsewhere as downstream regression checks or presentation values; they are not injected as inputs to cohort construction.

The source data are not vendored in this repository. Full execution therefore requires retrieval of the referenced public NHANES and mortality files. `tables/s3d_nhanes_input_manifest.csv`, `tables/s3d_regeneration_manifest.json`, `tables/cohort_flow.csv`, and `data/ARTIFACT_MANIFEST.tsv` record the prior regenerated inputs, output hashes, and resulting counts. This external-input dependency is the remaining provenance boundary; it is not an unresolved numerical discrepancy.

## Closure statement

No further PhysioRisk scientific changes are authorized unless new evidence reveals a substantive error.
