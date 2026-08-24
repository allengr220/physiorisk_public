# Sprint 3 summary

## 1. Repository changes performed

- Renamed and renumbered the seven canonical notebooks to match the requested dependency order.
- Added the previously root-level scoring notebook as `notebooks/04_physiorisk_scoring.ipynb` without changing notebook content.
- Updated notebook-name references and separated canonical notebooks 01–07 from supplemental revision notebooks 08–09.
- Statically traced notebook inputs, outputs, consumers, committed artifacts, and known external hash-verified artifacts.
- Assessed existing outputs against documented BMC reviewer issues without running notebooks, changing analyses, altering coefficients, or revising manuscript claims.

## 2. Files created

- `docs/ARTIFACT_PROVENANCE.md`
- `docs/PIPELINE_AUDIT.md`
- `docs/PIPELINE_GRAPH.md`
- `docs/REVIEWER_RESPONSE_MATRIX.md`
- `docs/SPRINT3_GAP_ANALYSIS.md`
- `docs/SPRINT3_SUMMARY.md`

## 3. Remaining repository issues

- Notebook 01 writes a 1999–2016 dataset, while notebook 02 reads a differently named 1999–2018 dataset.
- Notebook 02 follows an older CRP-complete branch and does not produce `benchmark_levine_no_crp_cohort.parquet` for notebook 03.
- Canonical parquets, the frozen DemoRisk pickle/metadata, exact two-axis transformation state, and several submitted table exports are not committed.
- Notebook 06 requires `test_phenoage_compare_outputs.parquet`, which has no canonical producer.
- Notebooks retain private absolute Colab/Google Drive paths.
- Notebook 07 ablation depends on unavailable older v1/v2/v3 scored artifacts and is not demonstrably an ablation of the submitted two-axis model.
- The verbatim BMC decision letter/reviewer reports are absent, so the response matrix uses the consolidated reviewer questions documented by Sprint 2 and does not invent reviewer numbering or quotations.

## 4. Reviewer criticisms already answered by existing outputs

Existing committed results address bootstrap C-index uncertainty and paired contrasts; censoring-robust discrimination; proportional-hazards testing; scaled Schoenfeld residuals and time interaction; temporal follow-up support; fixed-horizon calibration plots/data, calibration-in-the-large, intercept/slope point estimates, and Brier scores; convergence-controlled PhysioRisk evaluation; retained-benchmark cohort flow and cycle missingness; and common-cohort comparator sensitivity. These results should be incorporated into a future manuscript response, not recomputed.

## 5. Criticisms requiring new notebook work

New computation is still needed for a complete source-to-analysis cohort flow, valid included-versus-excluded characteristics, any upstream missing-data/imputation sensitivity, confidence intervals for fixed-horizon calibration intercepts/slopes if required, a submitted-two-axis-specific ablation if demanded, and external validation. Several of these first require recovery of missing frozen artifacts and upstream lineage.

## 6. Canonical public-artifact assessment

**Not yet fully suitable as the canonical self-contained reproducibility artifact.** It is now substantially more suitable as the canonical audit and provenance record: the notebook sequence is explicit, major artifacts are mapped, existing reviewer coverage is identified, and unresolved gaps are visible. A clean clone still cannot reproduce the analysis end to end, so public claims should describe it as an auditable but incomplete reproducibility package until the pipeline failures in `PIPELINE_AUDIT.md` are resolved.

## Existing coverage checklist

| Reviewer-requested item | Finding | Evidence and limitation |
|---|---|---|
| Cohort flow | PARTIALLY FOUND | `tables/cohort_flow.csv`; `notebooks/09_cohort_comparator_sensitivity.ipynb`. Begins at the preselected 19,829-person benchmark; upstream exclusions are unknown. |
| Missingness analysis | PARTIALLY FOUND | `tables/missingness_by_cycle.csv`; notebook 09. Zero missingness is only within the retained complete benchmark. |
| Comparator sensitivity | FOUND | `tables/comparator_sensitivity.csv`; notebook 09. Common complete-case comparison exists; imputation is a documented no-op in retained data. |
| Proportional hazards diagnostics | FOUND | `tables/ph_diagnostics.csv`, `tables/ph_time_interaction.csv`; notebook 08. |
| Schoenfeld residuals | FOUND | `tables/ph_schoenfeld_residuals.csv`; summarized by notebook 08 and Sprint 2 findings. |
| Calibration plots | FOUND | `tables/calibration_plot_data.csv`; plotted in `notebooks/08_validation_v2.ipynb`. No standalone committed image. |
| Calibration intercept/slope | FOUND | `tables/calibration_fixed_horizons.csv`. Fixed-horizon point estimates plus global slope interval; no fixed-horizon bootstrap intervals. |
| Bootstrap confidence intervals | FOUND | `tables/validation_v2.csv`, `tables/cindex_bootstrap_contrasts.csv`; 2,000 replicates with recorded seed. |
| C-index contrasts | FOUND | `tables/cindex_bootstrap_contrasts.csv`. |
| Temporal validation | FOUND | `notebooks/05_physiorisk_model_validation.ipynb`, `notebooks/08_validation_v2.ipynb`, `tables/validation_v2.csv`, `tables/followup_summary.csv`. Internal temporal, not external. |
| Ablation analyses | PARTIALLY FOUND | `notebooks/07_ablation_analysis_optional.ipynb` contains code, but outputs and required v1/v2/v3 inputs are absent and lineage differs from the submitted two-axis model. |
| Notebook provenance | FOUND | `docs/ARTIFACT_PROVENANCE.md`, `docs/PIPELINE_AUDIT.md`, and `docs/PIPELINE_GRAPH.md`; provenance gaps are explicitly labeled. |
| Reproducibility documentation | PARTIALLY FOUND | README, data/model docs, environment, provenance, and audit now exist; missing inputs, private paths, and broken handoffs prevent end-to-end reproducibility. |
