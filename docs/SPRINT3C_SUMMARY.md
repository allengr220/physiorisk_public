# Sprint 3C summary

## 1. Changes performed

- Replaced the wrong CRP-complete/three-axis notebook 02 with the recovered Levine-no-CRP cohort builder, byte-for-byte from the development archive.
- Confirmed notebook 01 is the correct V3 1999–2016 builder.
- Confirmed notebook 04 is the correct frozen-baseline two-axis scoring notebook.
- Preserved the more complete numbered notebook 05 containing the verified row-level comparator export.
- Removed the leftover top-level Windows `Zone.Identifier` metadata sidecar; no top-level `.ipynb` duplicate remains.
- Added a Git-safe data/artifact manifest and updated pipeline/provenance documentation.
- Did not run notebooks, change coefficients, change claims, or add datasets.

## 2. Notebook changes

| Public notebook | Sprint 3C action |
|---|---|
| `01_nhanes_extended_dataset_builder.ipynb` | Kept; correct V3 source already installed. |
| `02_benchmark_dataset_builder.ipynb` | Replaced with `benchmark_levine_no_crp_cohort_builder.ipynb`; exact source hash `612a52cb...b978c103`. |
| `03_demographic_risk_model.ipynb` | Kept; correct no-CRP split-aware DemoRisk builder. |
| `04_physiorisk_scoring.ipynb` | Kept; correct scoring producer already installed. |
| `05_physiorisk_model_validation.ipynb` | Preserved more complete public copy with aggregate and row-level exports. |
| `06_physiorisk_figures.ipynb` | Kept; correct figure producer. |
| `07_ablation_analysis_optional.ipynb` | Kept and documented as optional historical/supporting branch. |

## 3. No-CRP cohort producer

`notebooks/02_benchmark_dataset_builder.ipynb` now consumes notebook 01's `nhanes_1999_2016_extended_mortality_model_dataset.parquet` and explicitly writes `benchmark_levine_no_crp_cohort.parquet`.

## 4. Scored PhysioRisk producer

`notebooks/04_physiorisk_scoring.ipynb` explicitly writes the frozen-baseline Levine-no-CRP train and test scored parquets.

## 5. Row-level comparator producer

`notebooks/05_physiorisk_model_validation.ipynb` now explicitly exports `SEQN`, `PhenoAge_noCRP_proxy`, and `PhenoAgeAccel` to `test_phenoage_compare_outputs.parquet`. This artifact is no longer orphaned.

## 6. Duplicate cleanup

No root-level `.ipynb` file remained at inspection time. The complete validation content was already present in numbered notebook 05. The only remnant was an untracked Windows zone metadata sidecar, which was removed after confirming it contained no notebook content.

## 7. Pipeline result

**PASS_WITH_EXTERNAL_ARTIFACTS** for the minimum direct manuscript pipeline, notebooks 01–06. Every direct input has a public-source regeneration route, an upstream producer, or an external manifest entry; every major direct output has a documented producer.

Notebook 07 remains `PARTIAL` as an optional historical ablation branch. Standalone manuscript Table 1 source provenance also remains partial.

## 8. External Google Drive/MyDrive artifacts

External artifacts include the 1999–2016 analytic dataset, aligned no-CRP cohort, frozen baseline train/test parquets, DemoRisk pickle/metadata, scored train/test parquets, scoring metadata CSVs, aggregate comparison CSV, row-level comparator parquet, figure PDFs, and optional ablation exports. Exact expected paths and statuses are in `data/ARTIFACT_MANIFEST.tsv`.

The no-CRP benchmark and scored train/test parquets also have hash-verified WSL copies outside Git.

## 9. Unresolved provenance

- Exact standalone source/export for manuscript Table 1.
- Actual availability of several expected MyDrive artifacts has not been enumerated from WSL.
- The optional ablation notebook is not a submitted-two-axis ablation.

No major artifact in the direct notebook 01–06 chain has unresolved producer provenance.

## 10. Recommended next step before Sprint 4

Perform a non-computational MyDrive artifact inventory/export pass: record existence, size, SHA256, row/event counts where appropriate, and decide which small metadata/table artifacts can be safely committed. Then add a portable configuration/data-acquisition layer without editing frozen scientific logic. Only after that repository step should manuscript or new-analysis work begin.
