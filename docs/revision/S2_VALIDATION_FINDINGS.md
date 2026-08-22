# Sprint 2 validation findings

## Scope and locked inputs

All analyses use the frozen Sprint 1 `CalibratedTotalRisk` specification (`beta_Demo = 1.0586578127615558`, `beta_Physio = 0.3563514638575306`) and the canonical training/test artifacts. Notebook 08 verifies SHA256 hashes `e8f435...cbb86` (training) and `1455e2...d08ca` (temporal test), plus the retained benchmark hash `f53d03...e87125`, before analysis. No coefficient was selected, refit, or optimized from temporal-test performance. Historical submitted values remain separately labeled.

The temporal cohort contains 6,739 participants and 416 deaths. C-index intervals and paired contrasts use 2,000 participant-level bootstrap samples with seed 20260821.

## Reviewer questions

1. **Does CalibratedTotalRisk improve on DemoRisk beyond sampling uncertainty?**

   Yes in this internal temporal cohort. C-index is 0.84315 (bootstrap 95% CI 0.82180–0.86271) versus 0.82688 (0.80402–0.84694). The paired difference is 0.01628 (95% CI 0.01109–0.02199), and 100% of bootstrap differences are above zero.

2. **Is CalibratedTotalRisk distinguishable from PhenoAge NCP in discrimination?**

   No. CalibratedTotalRisk is only 0.00205 higher than the PhenoAge no-CRP proxy (0.84315 versus 0.84111); the paired 95% CI is −0.00326 to 0.00748 and 77.6% of bootstrap differences are above zero. The data do not establish a discrimination difference in either direction.

3. **Does PhysioRisk retain mortality information after correcting the non-converged HR?**

   Yes. The convergence-controlled HR per actual temporal-cohort SD is 1.387 (95% CI 1.338–1.439), with C-index 0.65411 (bootstrap 95% CI 0.62428–0.68503). The submitted HR of 2.772 is preserved only as historical/non-converged. PhysioRisk exceeds PhenoAge NCP acceleration in C-index by 0.01625, but its paired interval narrowly includes zero (−0.00049 to 0.03285; 97.0% of bootstrap differences above zero), so that contrast is suggestive rather than conclusive at the percentile-interval criterion.

4. **Are there important PH violations?**

   A material violation is present for CalibratedTotalRisk (rank-time Schoenfeld statistic 16.54, p=4.76×10⁻⁵). Scaled Schoenfeld residuals move from a negative mean early (−0.177 at 0–36 months) to positive means in middle (0.108 at 37–72 months) and late follow-up (0.161 after 72 months), indicating a progressively stronger association rather than a single late outlier region. A diagnostic extended Cox model with `score_z × log(time/60 months)` confirms this direction: interaction coefficient 0.171 per log-month ratio (95% CI 0.066–0.277, p=0.00150), equivalent to a 1.187-fold increase in HR per e-fold increase in time. Estimated HR/SD rises from 2.84 at 12 months to 3.74 at 60 months and 4.06 at 96 months. Reference interactions are smaller and non-significant for DemoRisk (0.084, p=0.238) and PhysioRisk (0.027, p=0.364). These are diagnostic temporal-cohort fits and do not replace the frozen model.

   The residual pattern is broad across follow-up but most clearly separates early negative from middle/late positive residuals. DemoRisk (PH-test p=0.087) and PhysioRisk (p=0.116) remain unflagged. HematologicStress (p=0.050) and RenalHepaticTurnover (p=0.038) do not meet the prespecified descriptive material flag of p<0.01.

5. **Is the corrected model acceptably calibrated at fixed horizons?**

   Calibration-in-the-large is close at both horizons: at 5 years, mean predicted mortality is 4.610% versus KM-observed 4.653% (observed minus predicted 0.043 percentage points; O/E 1.009); at 8 years, 8.571% versus 8.826% (difference 0.255 percentage points; O/E 1.030). The global Cox calibration slope is 0.811 (95% CI 0.762–0.859), but it assumes a constant score effect and therefore is not cleanly interpretable as a single degree of over-dispersion given the demonstrated time-varying effect. It may reflect temporal transport, non-proportionality, or other miscalibration—not simply model overfitting.

   Standard IPCW-weighted logistic calibration models at each fixed horizon give slopes of 0.941 at 5 years and 0.999 at 8 years (intercepts −0.101 and 0.067). These horizon-specific results are more reassuring than the global Cox slope and are compatible with good fixed-horizon calibration. They are evaluation diagnostics, not temporal recalibration, and currently have no bootstrap confidence intervals.

6. **What do the Brier/calibration results add beyond C-index?**

   IPCW Brier scores are 0.03776 at 5 years and 0.06018 at 8 years. Unlike C-index, these quantify absolute probability error under censoring. The larger eight-year value reflects the longer prediction horizon and greater accumulated event risk; it should not alone be treated as proof of worsening calibration. Calibration-in-the-large, horizon-specific slopes, and plot data directly assess agreement of predicted and observed risks. The censoring distribution for Brier and horizon-calibration evaluation is estimated in the temporal cohort; baseline survival and coefficients remain training-derived.

7. **Do common missing-data rules materially change the PhysioRisk versus PhenoAge NCP comparison?**

   No within the retained benchmark. Every retained participant has all required no-CRP proxy and PhysioRisk biomarkers, so the common complete-case analysis includes all 6,739 temporal participants and reproduces C-indices 0.65411 and 0.84111. A common training-derived-imputation sensitivity is necessarily a no-op on these data and gives the same results. Extending imputation to participants excluded before the retained benchmark is not possible without the missing frozen physiology residualization/axis parameters and could amount to model redevelopment.

8. **Are there subgroup/cohort-selection concerns that materially limit the manuscript?**

   Yes, chiefly provenance rather than an observed within-benchmark imbalance. The earliest retained benchmark already contains 19,829 adults with usable survival data and complete required biomarkers; it splits exactly into 13,090 training and 6,739 temporal participants. Consequently, source NHANES counts and exclusions before adult eligibility, mortality linkage, and biomarker completeness cannot be reconstructed, and included-versus-excluded characteristics upstream cannot be compared. Missingness by cycle is zero only *within this preselected retained benchmark* and must not be generalized to the source NHANES population.

9. **Which requests are fully addressed, partially addressed, or outstanding?**

   - **Fully addressed:** Harrell C-index with bootstrap uncertainty; convergence-controlled HR/SD with confidence intervals; paired C-index contrasts; Uno's IPCW C and cumulative/dynamic AUC; PH tests, scaled Schoenfeld residual data, and diagnostic log-time interactions; follow-up/risk-set characterization; frozen-training fixed-horizon absolute risk; calibration-in-the-large, global and horizon-specific slope diagnostics, plot data, and IPCW Brier scores; retained-cohort flow; biomarker-by-cycle missingness; common complete-case comparator analysis.
   - **Partially addressed:** eight-year calibration is supported by 1,137 participants still at risk and 410 deaths observed by 96 months, but the tail is less precise; cohort flow and included/excluded comparison begin only at the retained preselected benchmark; common imputation is a no-op in retained complete data and cannot recover upstream exclusions.
   - **Outstanding:** complete upstream NHANES flow and excluded-participant characteristics; exact frozen physiology residualization/axis artifacts needed for any defensible upstream imputation sensitivity; external validation; uncertainty intervals for the horizon-specific calibration slopes if reviewers require them.

## Censoring-robust discrimination addendum

`scikit-survival` 0.28.0 estimates the censoring distribution from all 13,090 training participants (1999–2010) and evaluates scores in all 6,739 temporal participants. At 5/8 years, respectively, Uno's truncated IPCW C is 0.823/0.827 for DemoRisk, 0.654/0.654 for PhysioRisk, 0.839/0.843 for CalibratedTotalRisk, 0.838/0.841 for PhenoAge NCP, and 0.641/0.638 for PhenoAge NCP acceleration. Corresponding cumulative/dynamic AUCs are 0.834/0.853, 0.657/0.677, 0.850/0.870, 0.850/0.875, and 0.655/0.698.

These censoring-robust metrics preserve the original discrimination conclusions: CalibratedTotalRisk clearly ranks better than DemoRisk, remains very close to the PhenoAge no-CRP proxy, and PhysioRisk carries modest discrimination beyond chance. No addendum result changes model specification or establishes external validity.

## Follow-up support

Temporal follow-up has reverse-KM median 74 months; empirical median 71 months, IQR 53–90, and maximum 111 months. There are 4,461 participants at risk at 60 months and 1,137 at 96 months. Five-year validation is well supported. Eight-year validation is defensible but should carry a less-precise-tail qualification.

## Interpretation guardrails

These are internal temporal-validation results, not external validation. Discrimination, calibration-in-the-large, calibration slope, and PH/time-varying effects answer different questions and are not interchangeable. Strong rank discrimination does not negate the PH violation; near-one fixed-horizon slopes do not restore proportional hazards; and the global slope of 0.811 should not be reduced to an “overfitting” label. PhenoAge NCP is a no-CRP proxy throughout. No result in this package was used to modify the frozen model.
