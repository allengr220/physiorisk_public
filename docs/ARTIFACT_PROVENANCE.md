# Artifact provenance

## Status vocabulary

- **COMMITTED**: present in this repository.
- **EXTERNAL VERIFIED**: available in the local source-artifact audit with a recorded SHA256, but not committed.
- **GENERATED, NOT COMMITTED**: producer code exists, but the output is absent from Git.
- **EXTERNAL GOOGLE DRIVE**: producer and expected MyDrive path are known, but the artifact is not committed.
- **UNKNOWN**: no defensible producer trace is present.

Paths below are repository-relative unless explicitly described as external. Notebook numbers refer to the consolidated names.

## Core datasets and model artifacts

| Filename | Producing notebook | Consuming notebook(s) | Manuscript usage | Status |
|---|---|---|---|---|
| `nhanes_biomarker_master_verified.parquet` | `01_nhanes_extended_dataset_builder.ipynb` | Same notebook | Intermediate NHANES harmonization | GENERATED, NOT COMMITTED |
| `nhanes_mortality_2019_verified.parquet` | `01_nhanes_extended_dataset_builder.ipynb` | Same notebook | Mortality-linkage intermediate | GENERATED, NOT COMMITTED |
| `nhanes_1999_2016_survival_master.parquet` | `01_nhanes_extended_dataset_builder.ipynb` | Same notebook | Survival intermediate | GENERATED, NOT COMMITTED |
| `nhanes_1999_2016_extended_mortality_model_dataset.parquet` | `01_nhanes_extended_dataset_builder.ipynb` | `02_benchmark_dataset_builder.ipynb` | Analytic source dataset | REGENERABLE FROM PUBLIC SOURCES; not committed |
| `benchmark_levine_no_crp_cohort.parquet` | `02_benchmark_dataset_builder.ipynb` | `03_demographic_risk_model.ipynb`; `scripts/run_sprint2_validation.py` | Source cohort for submitted no-CRP lineage and post-review checks | EXTERNAL VERIFIED / EXTERNAL GOOGLE DRIVE; SHA256 `f53d03317a6ea123021e7e36d585f7d92ba6f198821f21b083adfcc4b8e87125` |
| `physiorisk_v1_frozen_baseline_{train,test}_levinenocrp.parquet` | `03_demographic_risk_model.ipynb` | `04_physiorisk_scoring.ipynb` | Frozen DemoRisk-scored cohorts | PRODUCER VERIFIED / EXTERNAL GOOGLE DRIVE |
| `baseline_risk_v1_temporal_fit_levinenocrp.pkl` | `03_demographic_risk_model.ipynb` | No explicit canonical consumer | Frozen DemoRisk model | PRODUCER VERIFIED / EXTERNAL GOOGLE DRIVE |
| `baseline_risk_v1_temporal_metadata_levinenocrp.json` | `03_demographic_risk_model.ipynb` | No explicit canonical consumer | DemoRisk specification metadata | PRODUCER VERIFIED / EXTERNAL GOOGLE DRIVE |
| `physiorisk_2axis_v1_train_scored_from_frozen_baseline_levinenocrp.parquet` | `04_physiorisk_scoring.ipynb` | `05_physiorisk_model_validation.ipynb`, `07_totalrisk_reconstruction.ipynb`, `scripts/run_sprint2_validation.py` | Training physiology axes, submitted score, and frozen calibration | EXTERNAL VERIFIED; SHA256 `e8f435b5a8b68dbb477f04bad280252f563b9323e9bc9dea4eb7e945c22cbb86` |
| `physiorisk_2axis_v1_test_scored_from_frozen_baseline_levinenocrp.parquet` | `04_physiorisk_scoring.ipynb` | `05_physiorisk_model_validation.ipynb`, `06_physiorisk_figures.ipynb`, `07_totalrisk_reconstruction.ipynb`, `scripts/run_sprint2_validation.py` | Submitted Table 2/Figure 2 and temporal validation | EXTERNAL VERIFIED; SHA256 `1455e24e8ca3e1f68eb58a779f7a4d48e46b8e54fa435ec00de5cf51256d08ca` |
| `physiorisk_2axis_v1_eval_from_frozen_baseline_levinenocrp.csv` | `04_physiorisk_scoring.ipynb` | None explicit | Development evaluation | GENERATED, NOT COMMITTED |
| `physiorisk_2axis_v1_cohort_flow_levinenocrp.csv` | `04_physiorisk_scoring.ipynb` | None explicit | Scoring-stage flow | GENERATED, NOT COMMITTED |
| `physiorisk_2axis_v1_axis_membership.csv` | `04_physiorisk_scoring.ipynb` | None explicit | Methods/axis definition support | GENERATED, NOT COMMITTED |
| `physiorisk_2axis_v1_physio_cox_coefficients.csv` | `04_physiorisk_scoring.ipynb` | None explicit | Methods/model coefficients support | GENERATED, NOT COMMITTED |
| `test_phenoage_compare_outputs.parquet` | `05_physiorisk_model_validation.ipynb` | `06_physiorisk_figures.ipynb` | Row-level PhenoAge NCP and PhenoAge NCP acceleration values for Figure 1 | PRODUCER VERIFIED / EXTERNAL GOOGLE DRIVE; explicit export cell present |

## Manuscript figures and tables

| Filename | Producing notebook | Consuming notebook(s) | Manuscript usage | Status |
|---|---|---|---|---|
| `figures/Fig1.png`, `figures/Fig1.tiff` | `06_physiorisk_figures.ipynb` | Manuscript assembly outside notebooks | Figure 1, Kaplan–Meier survival by PhysioRisk and PhenoAge NCP acceleration quartiles | COMMITTED; notebook also exports PDF externally |
| `figures/Fig2.png`, `figures/Fig2.tiff` | `06_physiorisk_figures.ipynb` | Manuscript assembly outside notebooks | Figure 2, temporal benchmark visualization | COMMITTED |
| Manuscript Table 1 (embedded in `manuscript/PhysioRisk_BMC_MIDM_v2.{docx,pdf}`) | Manuscript assembly; source-cycle counts are not exported as a standalone table | Manuscript | Original NHANES cycle counts | COMMITTED only inside manuscript; no standalone provenance artifact |
| `physiorisk_vs_phenoage_aligned_comparison.csv` | `05_physiorisk_model_validation.ipynb` | `06_physiorisk_figures.ipynb`; manuscript assembly | Submitted Table 2 benchmark values | PRODUCER VERIFIED / EXTERNAL GOOGLE DRIVE; embedded notebook output is also available |
| `physiorisk_ablation_v1_metrics.csv`, `physiorisk_ablation_v1_cindex.csv`, `physiorisk_ablation_v1_hr.csv`, `physiorisk_ablation_v1_corr_age.csv` | `07_ablation_analysis_optional.ipynb` | Manuscript/supporting-material assembly outside notebooks | Optional ablation/sensitivity tables | GENERATED, NOT COMMITTED |

## Reconstruction, validation, and calibration outputs

`scripts/run_sprint2_validation.py` is the computational producer of the Sprint 2 tables. Notebooks 08 and 09 are display/report notebooks, not their producer.

| Filename | Producing code | Consuming notebook(s) | Manuscript/reviewer usage | Status |
|---|---|---|---|---|
| `tables/totalrisk_raw_identity_diagnostics.csv` | `07_totalrisk_reconstruction.ipynb` | Documentation | Raw-score reconstruction limitation | COMMITTED |
| `tables/totalrisk_training_coefficients.csv` | `07_totalrisk_reconstruction.ipynb` | `scripts/run_sprint2_validation.py`, documentation | Frozen training-only TotalRisk calibration | COMMITTED |
| `tables/totalrisk_reconstruction_comparison.csv` | `07_totalrisk_reconstruction.ipynb` | Documentation | Submitted versus corrected score comparison | COMMITTED |
| `tables/validation_v2.csv` | `scripts/run_sprint2_validation.py` | `08_validation_v2.ipynb` | C-index/HR validation with uncertainty | COMMITTED |
| `tables/cindex_bootstrap_contrasts.csv` | `scripts/run_sprint2_validation.py` | `08_validation_v2.ipynb` | Bootstrap C-index intervals and paired contrasts | COMMITTED |
| `tables/censoring_robust_discrimination.csv` | `scripts/run_sprint2_validation.py` | Documentation | Uno C and cumulative/dynamic AUC sensitivity | COMMITTED |
| `tables/ph_diagnostics.csv` | `scripts/run_sprint2_validation.py` | `08_validation_v2.ipynb` | Proportional-hazards diagnostics | COMMITTED |
| `tables/ph_schoenfeld_residuals.csv` | `scripts/run_sprint2_validation.py` | Documentation | Scaled Schoenfeld residual-level output | COMMITTED |
| `tables/ph_time_interaction.csv` | `scripts/run_sprint2_validation.py` | Documentation | Diagnostic time-varying effect analysis | COMMITTED |
| `tables/followup_summary.csv` | `scripts/run_sprint2_validation.py` | `08_validation_v2.ipynb` | Follow-up and horizon support | COMMITTED |
| `tables/calibration_fixed_horizons.csv` | `scripts/run_sprint2_validation.py` | `08_validation_v2.ipynb` | Calibration-in-the-large, intercept/slope, Brier scores | COMMITTED |
| `tables/calibration_plot_data.csv` | `scripts/run_sprint2_validation.py` | `08_validation_v2.ipynb` | Five- and eight-year calibration plots/data | COMMITTED; plotted in notebook output, no standalone image |
| `tables/cohort_flow.csv` | `scripts/run_sprint2_validation.py` | `09_cohort_comparator_sensitivity.ipynb` | Retained-benchmark flow | COMMITTED; upstream source flow remains unknown |
| `tables/cohort_included_excluded_characteristics.csv` | `scripts/run_sprint2_validation.py` | Documentation | Retained-cohort inclusion comparison | COMMITTED; excluded group is empty because upstream exclusions predate the available cohort |
| `tables/missingness_by_cycle.csv` | `scripts/run_sprint2_validation.py` | `09_cohort_comparator_sensitivity.ipynb` | Missingness by cycle | COMMITTED; limited to retained benchmark |
| `tables/comparator_sensitivity.csv` | `scripts/run_sprint2_validation.py` | `09_cohort_comparator_sensitivity.ipynb` | Complete-case/imputation comparator sensitivity | COMMITTED; imputation is a no-op in the retained complete cohort |

## Provenance limitations

The direct notebook 01–06 producer graph is now resolved. Large/person-level artifacts and several small exports remain external in Google Drive/MyDrive rather than Git; this is an availability limitation, not an orphaned-producer failure. Remaining provenance gaps are the standalone source for manuscript Table 1 and the absence from WSL/Git of the exact frozen DemoRisk model/metadata and scoring metadata exports. Private absolute Colab paths also remain. No data were regenerated or scientific code rewritten in this sprint.

The older 1999–2018 CRP-complete/three-axis notebook formerly copied as notebook 02 remains documented in `SOURCE_NOTEBOOK_PROVENANCE_AUDIT.md` as historical and is not part of the repaired canonical chain. See `data/ARTIFACT_MANIFEST.tsv` for the complete storage/status inventory.
