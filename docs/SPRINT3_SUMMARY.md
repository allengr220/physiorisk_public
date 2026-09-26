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

- Sprint 3C resolved the former notebook 01/02 mismatch by installing the recovered no-CRP cohort builder as notebook 02.
- Canonical parquets, the frozen DemoRisk pickle/metadata, exact two-axis transformation state, and several submitted table exports are not committed.
- Notebook 05 now has a verified producer cell for `test_phenoage_compare_outputs.parquet`; the artifact remains external in MyDrive.
- Notebooks retain private absolute Colab/Google Drive paths.
- Notebook 07 ablation depends on unavailable older v1/v2/v3 scored artifacts and is not demonstrably an ablation of the submitted two-axis model.
- The verbatim BMC decision letter/reviewer reports are absent, so the response matrix uses the consolidated reviewer questions documented by Sprint 2 and does not invent reviewer numbering or quotations.

## 4. Reviewer criticisms already answered by existing outputs

Existing committed results address bootstrap C-index uncertainty and paired contrasts; censoring-robust discrimination; proportional-hazards testing; scaled Schoenfeld residuals and time interaction; temporal follow-up support; fixed-horizon calibration plots/data, calibration-in-the-large, intercept/slope point estimates, and Brier scores; convergence-controlled PhysioRisk evaluation; retained-benchmark cohort flow and cycle missingness; and common-cohort comparator sensitivity. These results were incorporated into the revised manuscript without recomputation.

## 5. Criticisms requiring new notebook work

New computation is still needed for a complete source-to-analysis cohort flow, valid included-versus-excluded characteristics, any upstream missing-data/imputation sensitivity, confidence intervals for fixed-horizon calibration intercepts/slopes if required, a submitted-two-axis-specific ablation if demanded, and external validation. Several of these first require recovery of missing frozen artifacts and upstream lineage.

## 6. Canonical public-artifact assessment

**Suitable as the canonical auditable code/provenance artifact, but not a self-contained data bundle.** Sprint 3C completed the direct notebook 01–06 producer graph. A clean clone still requires external Google Drive/MyDrive artifacts, so the correct audit classification is `PASS_WITH_EXTERNAL_ARTIFACTS`, not fully self-contained reproduction.

## Existing coverage checklist

| Reviewer-requested item | Finding | Evidence and limitation |
|---|---|---|
| Cohort flow | PARTIALLY FOUND | `tables/cohort_flow.csv`; `notebooks/09_cohort_comparator_sensitivity.ipynb`. Begins at the preselected 19,829-person benchmark; upstream exclusions are unknown. |
| Missingness analysis | PARTIALLY FOUND | `tables/missingness_by_cycle.csv`; notebook 09. Zero missingness is only within the retained complete benchmark. |
| Comparator sensitivity | FOUND | `tables/comparator_sensitivity.csv`; notebook 09. Common complete-case comparison exists; imputation is a documented no-op in retained data. |
| Proportional hazards diagnostics | FOUND | `tables/ph_diagnostics.csv`, `tables/ph_time_interaction.csv`; notebook 08. |
| Schoenfeld residuals | GENERATED, NOT DISTRIBUTED | `tables/ph_schoenfeld_residuals.csv` is reproducible with `scripts/run_sprint2_validation.py` but intentionally excluded from the public release because it contains event-level derived records; aggregate findings remain documented. |
| Calibration plots | FOUND | `tables/calibration_plot_data.csv`; plotted in `notebooks/08_validation_v2.ipynb`. No standalone committed image. |
| Calibration intercept/slope | FOUND | `tables/calibration_fixed_horizons.csv`. Fixed-horizon point estimates plus global slope interval; no fixed-horizon bootstrap intervals. |
| Bootstrap confidence intervals | FOUND | `tables/validation_v2.csv`, `tables/cindex_bootstrap_contrasts.csv`; 2,000 replicates with recorded seed. |
| C-index contrasts | FOUND | `tables/cindex_bootstrap_contrasts.csv`. |
| Temporal validation | FOUND | `notebooks/05_physiorisk_model_validation.ipynb`, `notebooks/08_validation_v2.ipynb`, `tables/validation_v2.csv`, `tables/followup_summary.csv`. Internal temporal, not external. |
| Ablation analyses | PARTIALLY FOUND | `notebooks/07_ablation_analysis_optional.ipynb` contains code, but outputs and required v1/v2/v3 inputs are absent and lineage differs from the submitted two-axis model. |
| Notebook provenance | FOUND | `docs/ARTIFACT_PROVENANCE.md`, `docs/PIPELINE_AUDIT.md`, and `docs/PIPELINE_GRAPH.md`; provenance gaps are explicitly labeled. |
| Reproducibility documentation | FOUND | README, data/model docs, environment, provenance audit, artifact manifest, and a complete direct producer graph now exist; external artifacts and private paths still limit clean-clone execution. |
