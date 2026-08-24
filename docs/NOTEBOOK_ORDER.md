# Notebook order

The canonical dependency order is:

1. `01_nhanes_extended_dataset_builder.ipynb`
   - Builds the extended NHANES mortality-linked analytic dataset.

2. `02_benchmark_dataset_builder.ipynb`
   - Constructs the benchmark/aligned analysis dataset.

3. `03_demographic_risk_model.ipynb`
   - Builds the frozen age/sex DemoRisk Cox model.

4. `04_physiorisk_scoring.ipynb`
   - Fits the frozen two-axis physiology score from frozen baseline-scored inputs and exports scored train/test cohorts.

5. `05_physiorisk_model_validation.ipynb`
   - Runs the submitted PhysioRisk versus PhenoAge NCP comparison.

6. `06_physiorisk_figures.ipynb`
   - Generates final manuscript figures and related outputs.

7. `07_ablation_analysis_optional.ipynb`
   - Optional ablation/supporting analysis.

Supplemental post-review notebooks are retained after the canonical sequence:

8. `08_validation_v2.ipynb`
   - Displays the frozen-model validation, discrimination, PH, follow-up, and calibration outputs produced by `scripts/run_sprint2_validation.py`.

9. `09_cohort_comparator_sensitivity.ipynb`
   - Displays cohort flow, retained-cohort missingness, and comparator-sensitivity outputs produced by `scripts/run_sprint2_validation.py`.

The canonical sequence is not currently end-to-end executable from committed files. See `PIPELINE_AUDIT.md` for the precise breaks and `ARTIFACT_PROVENANCE.md` for artifact status.
