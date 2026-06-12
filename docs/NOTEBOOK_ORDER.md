# Notebook order

Run the notebooks in this order:

1. `01_nhanes_extended_dataset_builder.ipynb`
   - Builds the extended NHANES mortality-linked analytic dataset.

2. `02_benchmark_dataset_builder.ipynb`
   - Constructs the benchmark/aligned analysis dataset.

3. `03_demographic_risk_model.ipynb`
   - Builds the frozen age/sex DemoRisk Cox model.

4. `04_physiorisk_model_validation.ipynb`
   - Runs the main PhysioRisk vs PhenoAge NCP comparison.

5. `05_physiorisk_figures.ipynb`
   - Generates final manuscript figures and related outputs.

6. `06_ablation_analysis_optional.ipynb`
   - Optional ablation/supporting analysis.
