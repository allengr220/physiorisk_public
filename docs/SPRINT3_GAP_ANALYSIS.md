# Sprint 3 gap analysis

## Decision rule

This classification is conservative and does not treat embedded notebook output, a retained-cohort proxy, or an older model branch as satisfying a broader reviewer request. No new analysis was performed.

## A. Already satisfied by existing analyses

- Temporal-test discrimination with participant-level bootstrap 95% intervals (`tables/validation_v2.csv`).
- Paired C-index contrasts for CalibratedTotalRisk versus DemoRisk and PhenoAge NCP, and PhysioRisk versus PhenoAge NCP acceleration (`tables/cindex_bootstrap_contrasts.csv`).
- Censoring-robust discrimination sensitivity using Uno C and cumulative/dynamic AUC (`tables/censoring_robust_discrimination.csv`).
- Proportional-hazards tests, event-level scaled Schoenfeld residuals, and diagnostic score-by-log-time interactions (`tables/ph_diagnostics.csv`, locally generated `tables/ph_schoenfeld_residuals.csv`, and `tables/ph_time_interaction.csv`). The event-level residual file is reproducible but intentionally not distributed in the public release.
- Five- and eight-year calibration-in-the-large, global calibration slope with interval, fixed-horizon calibration intercept/slope point estimates, IPCW Brier score, and plot data (`tables/calibration_fixed_horizons.csv`, `tables/calibration_plot_data.csv`).
- Follow-up and risk-set support for temporal validation (`tables/followup_summary.csv`).
- Common complete-case comparator sensitivity within the retained benchmark; training-derived imputation is demonstrably a no-op there (`tables/comparator_sensitivity.csv`).
- Convergence-controlled PhysioRisk HR/SD re-evaluation and frozen training-only TotalRisk calibration (`tables/validation_v2.csv`, `tables/totalrisk_training_coefficients.csv`).

These analyses should be reported rather than rerun.

## B. Require manuscript rewriting only

- Describe the validation accurately as an internal temporal NHANES split, not external validation.
- State that PhenoAge NCP is a no-CRP proxy and interpret the non-significant paired discrimination contrast correctly.
- Add the existing bootstrap uncertainty, PH violation, Schoenfeld pattern, calibration, follow-up, and comparator-sensitivity results to the appropriate Methods/Results/Discussion sections.
- Explain that near-one fixed-horizon calibration slopes do not negate the demonstrated time-varying score effect.
- Replace reliance on the historical non-converged PhysioRisk HR with the convergence-controlled result while preserving the submitted value as historical provenance.
- Reframe TotalRisk using the existing reconstruction/calibration evidence; avoid claiming that an uncalibrated sum of differently scaled components is automatically a Cox linear predictor.
- State the retained-cohort boundary: `cohort_flow.csv` and `missingness_by_cycle.csv` begin at the already selected 19,829-person benchmark and do not describe exclusions or missingness in source NHANES.
- Clarify the intended interpretive/decomposition contribution without strengthening manuscript claims.

## C. Require genuinely new computation

- **Complete upstream cohort flow:** reconstruct source NHANES eligibility, mortality-linkage, biomarker availability, and exclusion stages before the retained benchmark.
- **Included-versus-excluded comparison:** compute characteristics from the recovered upstream population; the current zero-excluded table cannot answer this question.
- **Upstream missing-data sensitivity:** possible only after recovering the exact frozen residualization, axis-standardization, and physiology-model artifacts; otherwise it risks model redevelopment.
- **Horizon-specific calibration uncertainty:** bootstrap fixed-horizon intercept/slope estimates if the reviewer requires intervals rather than point estimates.
- **Submitted-model ablation:** the optional notebook analyzes older v1/v2/v3 inputs and has no committed outputs. It should not be assumed to answer ablation questions about the submitted two-axis model.
- **External validation:** requires an independent cohort and is not present in this repository.

## Repository work required before new computation

Sprint 3C resolved the notebook 01/02 contract and recovered the producer of `benchmark_levine_no_crp_cohort.parquet`. Remaining prerequisites are to inventory/export the canonical Google Drive/MyDrive artifacts, recover exact frozen model/transformation state, and replace private Colab paths with documented configuration in a later non-scientific reproducibility sprint. These steps must preserve the frozen historical analysis and precede upstream sensitivity work.
