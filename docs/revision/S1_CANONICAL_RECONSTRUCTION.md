# Sprint 1 canonical reconstruction

## Status and evidence labels

- **FACT**: directly present in a checked-in notebook, its embedded output, the submitted manuscript, or repository history.
- **INFERENCE**: a conclusion supported by multiple facts but not directly recorded as an artifact.
- **UNKNOWN**: required provenance or parameter is absent and cannot be recovered without the missing data/model artifact.

This audit is tied to repository commit `17c1d33` and the six submitted-analysis notebooks at that commit. No submitted notebook was modified.

## Canonical path and exact lineage

1. **FACT** — `notebooks/01_nhanes_extended_dataset_builder.ipynb` downloads and harmonizes NHANES cycle files, merges the 2019 public linked-mortality fixed-width files by `SEQN`, limits survival analysis to 1999–2016, and writes `nhanes_1999_2016_extended_mortality_model_dataset.parquet`. The output is not committed.
2. **FACT** — the aligned validation path uses training cycles 1999–2010 (implemented as `cycle_start_year <= 2009` in notebook 02 and as `<= 2010` in notebook 03, equivalent for biennial cycle start years) and temporal-test cycles 2011–2016 (`>= 2011`).
3. **FACT** — `notebooks/03_demographic_risk_model.ipynb` consumes `benchmark_levine_no_crp_cohort.parquet`, fits the frozen demographic model on training data, and writes baseline-scored train/test parquet files plus a model pickle and metadata JSON. None is committed.
4. **UNKNOWN** — the producer of `benchmark_levine_no_crp_cohort.parquet` is absent. Notebook 02 builds a different CRP-complete benchmark and therefore is not that producer.
5. **FACT** — the historical `physiorisk_2axis_v1_{train,test}_scored_from_frozen_baseline_levinenocrp.parquet` files are available locally outside Git and are the inputs consumed by notebook 04. **UNKNOWN** — their producer code/model remains absent. Notebook 04 explicitly says it does not rebuild PhysioRisk.
6. **FACT** — `notebooks/04_physiorisk_model_validation.ipynb` constructs the PhenoAge no-CRP proxy and its acceleration, then evaluates all five submitted Table 2 scores. Its embedded output is the direct producer trace available for Table 2.
7. **FACT** — `notebooks/05_physiorisk_figures.ipynb` reads the same scored test parquet and the table exported by notebook 04 to produce Figure 2; it does not fit scores.

## Score definitions

### DemoRisk

- **FACT** — model: Cox PH with `cr(RIDAGEYR, df=4) + C(RIAGENDR)`, duration `PERMTH_INT`, event `MORTSTAT`, `penalizer=0.01`, `l1_ratio=0.0`; fit on training only and frozen.
- **FACT** — notebook 03 creates a Patsy design with `formula + " - 1"`, fits lifelines `CoxPHFitter`, and defines `BaselineRisk = predict_log_partial_hazard(design)`. The manuscript and figures relabel `BaselineRisk` as DemoRisk.
- **DISCREPANCY (FACT)** — notebook 02's older benchmark path uses sklearn `SplineTransformer(n_knots=5, degree=3, include_bias=False)` rather than the manuscript/Patsy natural cubic spline `cr(age, df=4)`. It is not the Table 2 path.
- **UNKNOWN** — fitted DemoRisk coefficients and design knots are only in the missing pickle/design artifact and are not printed in the checked-in notebook output.

### Biomarker residualization and axes

- **FACT** — documented residualization model for every biomarker is ordinary least squares: `biomarker ~ cr(RIDAGEYR, df=4) + C(RIAGENDR)`, fit on training only and applied frozen to test.
- **FACT** — residuals are standardized with their training residual mean and sample SD (pandas default `ddof=1`) before signed averaging.
- **FACT** — `HematologicStress = mean(LBXWBCSI_resid_z, -LBXLYPCT_resid_z, LBXMCV_resid_z, LBXRDW_resid_z)`.
- **FACT** — `RenalHepaticTurnover = mean(LBXSCR_resid_z, -LBXSAL_resid_z, LBXSAPSI_resid_z)`.
- **INFERENCE** — the two axes were likely standardized again with training means/SDs before Cox fitting because the only checked-in axis-building implementation (the three-axis notebook 02 path) does so. The manuscript says the axes are averages of standardized residuals but does not explicitly state this second axis-standardization step.
- **UNKNOWN** — all biomarker regression intercepts/coefficients, spline design state, residual means/SDs, and any axis means/SDs from the submitted two-axis producer are missing.

### Raw and standardized PhysioRisk

- **FACT** — manuscript specification: `PhysioRisk_raw = 0.433 * HematologicStress + 0.235 * RenalHepaticTurnover`, where the printed coefficients are rounded.
- **FACT** — this is described as a penalized Cox LP fit on training data; the submitted two-axis producer, its exact coefficient precision, and its penalty are absent.
- **INFERENCE** — `penalizer=1.0`, `l1_ratio=0.0` is plausible because notebook 02 uses that setting for its three-axis physiology Cox model, but it cannot be asserted for the missing two-axis producer.
- **FACT** — `PhysioRisk_z = (PhysioRisk_raw - mean_train(PhysioRisk_raw)) / sd_train(PhysioRisk_raw)` and the transformation is frozen for test.
- **FACT** — stored training `PhysioRisk_2axis` has mean `-8.68501434084156e-18` and sample SD `1.0000000000000009`, confirming that it is the standardized score.
- **UNKNOWN** — the native raw-LP training mean and SD are absent. The files contain both axes but no raw LP. The rounded manuscript formula gives an approximate raw mean `-4.34250717042078e-18` and sample SD `0.2806779398439553`, but its restandardized values differ from the stored score (training maximum absolute error `0.003461808928022947`), so these are not exact canonical parameters.

### TotalRisk

- **FACT** — manuscript construction: `TotalRisk_original = DemoRisk + PhysioRisk_z`.
- **FACT** — notebook 04 consumes `TotalRisk_2axis`; it does not construct it. Its embedded metrics agree with manuscript Table 2.
- **FACT** — this mixes a native-scale Cox LP (DemoRisk) with a unit-SD physiology score. Consequently, the coefficient on the native raw physiological LP is implicitly `1 / sd_train(PhysioRisk_raw)`, not 1, and the composite is not generally the joint Cox LP claimed in the manuscript.

### PhenoAge NCP and acceleration

- **FACT** — after training-median imputation of the eight biomarker inputs, notebook 04 defines:

  `PhenoAge_NCP = -19.907 - 0.0336*LBXSAL + 0.0095*LBXSCR + 0.1953*log(LBXGLU) - 0.0120*LBXLYPCT + 0.0268*LBXMCV + 0.3306*LBXRDW + 0.0019*LBXSAPSI + 0.0554*LBXWBCSI + 0.0804*RIDAGEYR`.

- **FACT** — this is explicitly a no-CRP proxy, not full PhenoAge.
- **FACT** — `PhenoAge_NCP_acceleration = PhenoAge_NCP - prediction[OLS(PhenoAge_NCP ~ cr(age,df=4) + sex)]`; imputer and OLS are fit only in training and frozen for test.
- **UNKNOWN** — fitted imputation medians and acceleration-regression parameters are not exported or printed.

## Table 2 lineage

- **FACT** — notebook 04 loads the missing scored train/test parquets, reconstructs both PhenoAge comparators, standardizes each evaluated predictor within the evaluated cohort, fits an unpenalized univariable Cox model, and reports C-index, HR per one actual cohort SD with 95% CI, p-value, and Pearson correlation with age.
- **FACT** — its temporal-test embedded output has `N=6,739`, `deaths=416` and matches manuscript Table 2 after rounding: DemoRisk 0.826876 / 3.735672; PhysioRisk 0.654110 / 2.771658; TotalRisk 0.839760 / 1.877467; PhenoAge NCP 0.841108 / 3.976118; acceleration 0.637857 / 1.432148 (C-index / HR per SD).
- **DISCREPANCY (FACT)** — notebook 06 computes HR/SD with `penalizer=0.1`; notebook 04/Table 2 uses the default unpenalized Cox model. Notebook 06 is optional and is not the Table 2 producer.
- **DISCREPANCY (FACT)** — the manuscript calls the additive standardized construction a Cox log-risk recombination. This interpretation is mathematically unsupported unless its two component coefficients happen to equal one on those exact scales.
- **DISCREPANCY (FACT)** — under current lifelines, notebook 04's unpenalized PhysioRisk HR/SD fit emits a Newton–Raphson non-convergence warning, hidden by its global warning suppression, and returns HR `2.771658`. A convergence-controlled fit of the identical standardized predictor returns log-HR about `0.32748` (HR about `1.3875`). The other Table 2 HR fits converge and are stable. Thus the manuscript PhysioRisk HR/SD is not a valid converged estimate even though its predictor was correctly standardized.
- **FACT** — the revision comparison table preserves these as separate rows: `PhysioRisk_submitted` retains the historical Table 2 values, while `PhysioRisk_convergence_corrected` records the convergence-controlled re-evaluation. No historical value is overwritten.

## Local source-artifact audit (outside Git)

| Artifact | Bytes | SHA256 | Rows | Deaths | Columns |
|---|---:|---|---:|---:|---|
| `/home/ubuntu2204/longevity/data/physiorisk/data/benchmark_levine_no_crp_cohort.parquet` | 353,541 | `f53d03317a6ea123021e7e36d585f7d92ba6f198821f21b083adfcc4b8e87125` | 19,829 | 2,936 | 14 |
| `/home/ubuntu2204/longevity/data/physiorisk/data/physiorisk_2axis_v1_train_scored_from_frozen_baseline_levinenocrp.parquet` | 761,937 | `e8f435b5a8b68dbb477f04bad280252f563b9323e9bc9dea4eb7e945c22cbb86` | 13,090 | 2,520 | 19 |
| `/home/ubuntu2204/longevity/data/physiorisk/data/physiorisk_2axis_v1_test_scored_from_frozen_baseline_levinenocrp.parquet` | 390,061 | `1455e24e8ca3e1f68eb58a779f7a4d48e46b8e54fa435ec00de5cf51256d08ca` | 6,739 | 416 | 19 |

The benchmark columns are `SEQN`, `PERMTH_INT`, `MORTSTAT`, `RIDAGEYR`, `RIAGENDR`, `cycle_start_year`, `LBXSAL`, `LBXSCR`, `LBXGLU`, `LBXLYPCT`, `LBXMCV`, `LBXRDW`, `LBXSAPSI`, and `LBXWBCSI`. Each scored file adds `BaselineRisk`, `HematologicStress`, `RenalHepaticTurnover`, `PhysioRisk_2axis`, and `TotalRisk_2axis`.

`TotalRisk_2axis == BaselineRisk + PhysioRisk_2axis` exactly in every training and test row. Exact `PhysioRisk_raw` and therefore exact `TotalRisk_raw` remain unrecoverable without the unrounded two-axis coefficients/native standardization artifact.

Notebook 07 asserts both scored-file SHA256 hashes, row/death counts, exact cycle sets, all required columns, non-null unique `SEQN` within each cohort, and disjoint train/test `SEQN` sets before any model fitting. Rounded-coefficient raw-LP identity errors are exported to `tables/totalrisk_raw_identity_diagnostics.csv`.
