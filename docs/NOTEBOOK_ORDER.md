# Notebook order

The canonical dependency order is:

1. `01_nhanes_extended_dataset_builder.ipynb`
   - Builds the extended NHANES mortality-linked analytic dataset.

2. `02_benchmark_dataset_builder.ipynb`
   - Consumes notebook 01's 1999–2016 extended dataset and produces `benchmark_levine_no_crp_cohort.parquet`.

3. `03_demographic_risk_model.ipynb`
   - Builds the frozen age/sex DemoRisk Cox model.

4. `04_physiorisk_scoring.ipynb`
   - Fits the frozen two-axis physiology score from frozen baseline-scored inputs and exports scored train/test cohorts.

5. `05_physiorisk_model_validation.ipynb`
   - Runs the submitted PhysioRisk versus PhenoAge NCP comparison and exports the aggregate benchmark table plus row-level PhenoAge NCP/acceleration values for figures.

6. `06_physiorisk_figures.ipynb`
   - Generates final manuscript figures and related outputs.

7. `07_ablation_analysis_optional.ipynb`
   - Optional historical v1/v2/v3 ablation branch. It is not part of the minimum direct manuscript reproduction chain.

Supplemental post-review notebooks are retained separately from the numbered 01–07 sequence:

- `07_totalrisk_reconstruction.ipynb`
  - Reconstructs and diagnoses TotalRisk using the frozen scored parquets.

- `08_validation_v2.ipynb`
   - Displays the frozen-model validation, discrimination, PH, follow-up, and calibration outputs produced by `scripts/run_sprint2_validation.py`.

- `09_cohort_comparator_sensitivity.ipynb`
   - Displays cohort flow, retained-cohort missingness, and comparator-sensitivity outputs produced by `scripts/run_sprint2_validation.py`.

The producer graph is internally complete for notebooks 01–06. Large derived inputs/outputs remain external by design; see `PIPELINE_AUDIT.md`, `ARTIFACT_PROVENANCE.md`, and `EXPECTED_ARTIFACTS.md`.
