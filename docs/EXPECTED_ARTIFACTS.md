# Expected artifacts

The machine-readable inventory is `data/ARTIFACT_MANIFEST.tsv`. This document explains the public storage policy and minimum artifact contract without asserting that external files are present in a clean clone.

## Storage policy

- Git contains notebooks, documentation, compact tables, manuscript files, and final PNG/TIFF figures.
- Raw NHANES files and large participant-level derived parquets remain outside Git by design.
- Event-level diagnostic output `tables/ph_schoenfeld_residuals.csv` is intentionally not distributed in the public release; `scripts/run_sprint2_validation.py` reproduces it from the public workflow.
- `$MYDRIVE` means `/content/drive/MyDrive` under Google Colab.
- `external_google_drive` means the expected path and producer are documented, but the artifact is not committed.
- `regenerable_from_public_sources` means the producer notebook can rebuild the artifact from declared public NHANES inputs. It does not mean the notebook was rerun in Sprint 3C.

## Minimum direct-pipeline contract

| Stage | Required input | Expected output |
|---|---|---|
| 01 NHANES builder | Public NHANES and linked mortality sources | `nhanes_1999_2016_extended_mortality_model_dataset.parquet` |
| 02 no-CRP cohort builder | Stage 01 output | `benchmark_levine_no_crp_cohort.parquet` |
| 03 DemoRisk | Stage 02 output | Frozen baseline train/test parquets, model pickle, metadata JSON |
| 04 PhysioRisk scoring | Stage 03 train/test parquets | Frozen scored train/test parquets and scoring metadata tables |
| 05 comparison | Stage 04 scored parquets | Aggregate benchmark CSV and `test_phenoage_compare_outputs.parquet` |
| 06 figures | Stage 04 test parquet and both stage 05 outputs | Figure 1 and Figure 2 exports |

## Terminology contract

- DemoRisk ↔ `BaselineRisk`
- PhysioRisk ↔ `PhysioRisk_2axis`
- TotalRisk ↔ `TotalRisk_2axis`
- PhenoAge NCP ↔ `PhenoAge_noCRP_proxy`
- PhenoAge NCP acceleration ↔ `PhenoAgeAccel`

No column or artifact was renamed in Sprint 3C.

## External artifacts

The no-CRP benchmark and scored train/test parquets have hash-verified WSL copies outside the repository. Other producer-verified artifacts are believed to reside in Google Drive/MyDrive and are marked accordingly rather than invented or regenerated. The exact DemoRisk pickle/metadata, frozen baseline train/test parquets, scoring metadata CSVs, comparison CSV, and row-level comparator parquet should be exported or inventoried from MyDrive before a self-contained release is claimed.

## Known unresolved artifact

The only major manuscript artifact with unresolved producer provenance is the standalone source for manuscript Table 1. The table is committed inside the manuscript, but no exact standalone builder/export was identified. This does not break the notebook 01–06 data flow; it remains a documentation provenance gap.
