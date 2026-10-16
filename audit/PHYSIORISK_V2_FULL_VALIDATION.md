# PhysioRisk v2 Full Validation

## Scope and frozen lineage

This analysis was run from parent commit `effea63db3f47eba4e4d95656b3dce41cb2f94fe`. `PhysioRisk_2axis_v2`
is frozen from commit `7abcbc11a3eda981b2f4d88e385cb0486f1ed6d7`; `PhenoAge_NCP_v2` and its
acceleration are frozen from the parent commit. DemoRisk was joined by `SEQN`
and is bit-for-bit identical to the historical v1 participant values.

Development contains 13,090 participants and 2,520 deaths. Temporal validation
contains 6,739 participants and 416 deaths. Participant-ID sets are identical
across DemoRisk, PhysioRisk, and PhenoAge in each cohort. Input paths and SHA256
hashes are recorded in the machine-readable provenance record.

Neither frozen corrected component was refit. Cohort membership, temporal split,
model specifications, and the separate 1999–2000 assay-standardization
sensitivity were not changed.

## Development-only calibrated composite

The unpenalized development Cox model `mortality ~ DemoRisk +
PhysioRisk_2axis_v2` produced:

- `beta_Demo_v2 = 1.0650002857110228`
- `beta_Physio_v2 = 0.36101789273434753`

`CalibratedTotalRisk_v2 = beta_Demo_v2 * DemoRisk + beta_Physio_v2 *
PhysioRisk_2axis_v2`. Coefficients and development baseline survival were frozen
before any validation evaluation. The full baseline-survival step function and
lifelines centering constant are in
`outputs/physiorisk_v2_validation/calibrated_totalrisk_v2_baseline_survival.csv`.

## Historical unit-weight composite

`TotalRisk_original_v2 = DemoRisk + PhysioRisk_2axis_v2` was reconstructed only
for provenance and is not the primary composite.

| model | N | deaths | Harrell_C | HR_per_validation_SD | HR_95CI_low | HR_95CI_high | p_value | pearson_age_correlation |
|---|---|---|---|---|---|---|---|---|
| TotalRisk_original_v2 | 6739 | 416 | 0.84145868212 | 1.86966599988 | 1.80632907319 | 1.93522376569 | 2.1662290762e-277 | 0.79301492473 |

The independent approximate audit-target discrepancies (observed minus target)
were `-3.400012363941052e-05` for its HR/SD and
`-4.1317880172253574e-05` for its C-index.

## Primary validation metrics

| model | Harrell_C | Harrell_C_bootstrap_95CI_low | Harrell_C_bootstrap_95CI_high | HR_per_validation_SD | HR_95CI_low | HR_95CI_high | p_value | pearson_age_correlation |
|---|---|---|---|---|---|---|---|---|
| DemoRisk | 0.826875955625 | 0.804018299539 | 0.84693722264 | 3.73567398032 | 3.34676913203 | 4.169770766 | 4.37657027846e-122 | 0.969734021755 |
| PhysioRisk_2axis_v2 | 0.663181826219 | 0.632042118241 | 0.693889892071 | 1.38493336581 | 1.33542916001 | 1.43627268685 | 7.72929410744e-69 | 0.101657447838 |
| CalibratedTotalRisk_v2 | 0.844491088903 | 0.823192111487 | 0.864053587704 | 3.27048111148 | 3.04541667585 | 3.51217841072 | 9.89595696301e-233 | 0.941871455708 |
| PhenoAge_NCP_v2 | 0.844747938457 | 0.822721262079 | 0.864454837642 | 2.30958752528 | 2.20471373261 | 2.41944995309 | 5.08632049039e-273 | 0.923119642272 |
| PhenoAge_NCP_acceleration_v2 | 0.654344247268 | 0.621549982788 | 0.685449852385 | 1.2980041337 | 1.25647170976 | 1.34090940369 | 1.1059589788e-55 | 0.0508860611716 |

For CalibratedTotalRisk_v2, observed-minus-approximate-target discrepancies were
`-1.888852007470021e-05` for HR/SD and `-8.911097482799946e-06` for C-index.

## Paired C-index bootstrap

All contrasts used 2,000 participant-level paired replicates with seed 20260821.

| contrast | observed_delta_C_A_minus_B | percentile_95CI_low | percentile_95CI_high | bootstrap_failures | eventless_redraws |
|---|---|---|---|---|---|
| CalibratedTotalRisk_v2 - DemoRisk | 0.0176151332779 | 0.0119655056227 | 0.0236605267659 | 0 | 0 |
| CalibratedTotalRisk_v2 - PhenoAge_NCP_v2 | -0.000256849554096 | -0.00729374931416 | 0.0062613746301 | 0 | 0 |
| PhysioRisk_2axis_v2 - PhenoAge_NCP_acceleration_v2 | 0.00883757895099 | -0.0116038164324 | 0.0289245887881 | 0 | 0 |

## Fixed-horizon calibration

Absolute predictions use only the development coefficients and baseline
survival. Validation outcomes enter evaluation only. Fixed-horizon IPCW uses
the validation censoring Kaplan–Meier estimator; known outcomes contribute
directly and participants censored before the horizon do not supply an observed
binary outcome.

| horizon_months | mean_predicted_mortality | KM_observed_mortality | observed_to_expected_ratio | IPCW_logistic_calibration_intercept | IPCW_logistic_calibration_slope | IPCW_Brier_score |
|---|---|---|---|---|---|---|
| 60 | 0.0484515558541 | 0.0465326042846 | 0.960394428298 | -0.266566525457 | 0.894581033556 | 0.0377157424552 |
| 96 | 0.089335220578 | 0.0882555497602 | 0.987914387956 | -0.0603393139558 | 0.962575374301 | 0.0603691402659 |

Global Cox calibration slope: `0.8037928951265351` (95% CI
`0.7554275191482236` to `0.8521582711048465`;
p=`9.895956963008485e-233`).

## Proportional-hazards diagnostics

| model | test_statistic | p_value | descriptive_flag_p_lt_0_01 | scaled_residual_band_summary |
|---|---|---|---|---|
| DemoRisk | 2.925210348 | 0.08720585924 | False | early_0_36m: mean=-0.087; middle_37_72m: mean=0.044; late_73m_plus: mean=0.099 |
| PhysioRisk_2axis_v2 | 0.02412234086 | 0.8765740272 | False | early_0_36m: mean=0.010; middle_37_72m: mean=-0.028; late_73m_plus: mean=0.042 |
| CalibratedTotalRisk_v2 | 11.56936143 | 0.0006704743983 | True | early_0_36m: mean=-0.145; middle_37_72m: mean=0.079; late_73m_plus: mean=0.154 |
| PhenoAge_NCP_v2 | 0.07806320867 | 0.7799394521 | False | early_0_36m: mean=0.012; middle_37_72m: mean=-0.050; late_73m_plus: mean=0.086 |
| PhenoAge_NCP_acceleration_v2 | 1.006815508 | 0.3156669553 | False | early_0_36m: mean=0.029; middle_37_72m: mean=-0.043; late_73m_plus: mean=0.031 |

The diagnostic extended Cox result for CalibratedTotalRisk_v2 was:

| model | time_interaction_coefficient | time_interaction_95CI_low | time_interaction_95CI_high | time_interaction_p_value | direction |
|---|---|---|---|---|---|
| CalibratedTotalRisk_v2 | 0.129700960167 | 0.0292947176614 | 0.230107202672 | 0.0113476486457 | effect_strengthens_over_time |

## Censoring-robust discrimination

| model | horizon_months | Uno_C_IPCW_truncated_at_horizon | cumulative_dynamic_AUC_IPCW |
|---|---|---|---|
| DemoRisk | 60 | 0.8225044664 | 0.8337675555 |
| DemoRisk | 96 | 0.826827675 | 0.8531038126 |
| PhysioRisk_2axis_v2 | 60 | 0.6660334954 | 0.6653298157 |
| PhysioRisk_2axis_v2 | 96 | 0.6629794322 | 0.6823721053 |
| CalibratedTotalRisk_v2 | 60 | 0.8405752652 | 0.8508634862 |
| CalibratedTotalRisk_v2 | 96 | 0.8443331343 | 0.8699370432 |
| PhenoAge_NCP_v2 | 60 | 0.8414597846 | 0.8529521364 |
| PhenoAge_NCP_v2 | 96 | 0.8446443569 | 0.875015409 |
| PhenoAge_NCP_acceleration_v2 | 60 | 0.6633737241 | 0.6709687016 |
| PhenoAge_NCP_acceleration_v2 | 96 | 0.6542344015 | 0.6902284934 |

## Follow-up support

| horizon_months | reverse_KM_median_months | number_at_risk | deaths_observed_by_horizon |
|---|---|---|---|
| 60 | 74 | 4461 | 289 |
| 96 | 74 | 1137 | 410 |

## Historical versus corrected comparison

| model | historical_C | corrected_C | historical_HR_per_SD | corrected_HR_per_SD | historical_age_correlation | corrected_age_correlation |
|---|---|---|---|---|---|---|
| DemoRisk | 0.8268759556 | 0.8268759556 | 3.73567398 | 3.73567398 | 0.9697340218 | 0.9697340218 |
| PhysioRisk_2axis_v2 | 0.6541097325 | 0.6631818262 | 1.387468265 | 1.384933366 | 0.1062334525 | 0.1016574478 |
| CalibratedTotalRisk_v2 | 0.8431533308 | 0.8444910889 | 3.259001624 | 3.270481111 | 0.9464909892 | 0.9418714557 |
| PhenoAge_NCP_v2 | 0.8411083058 | 0.8447479385 | 3.976116202 | 2.309587525 | 0.9613694861 | 0.9231196423 |
| PhenoAge_NCP_acceleration_v2 | 0.6378574839 | 0.6543442473 | 1.432147455 | 1.298004134 | 0.03329887535 | 0.05088606117 |

| contrast | historical_delta_C | historical_95CI_low | historical_95CI_high | corrected_delta_C | corrected_95CI_low | corrected_95CI_high |
|---|---|---|---|---|---|---|
| CalibratedTotalRisk_v2 - DemoRisk | 0.01627737518 | 0.01109216474 | 0.0219872027 | 0.01761513328 | 0.01196550562 | 0.02366052677 |
| CalibratedTotalRisk_v2 - PhenoAge_NCP_v2 | 0.002045024982 | -0.003258220137 | 0.007479917024 | -0.0002568495541 | -0.007293749314 | 0.00626137463 |
| PhysioRisk_2axis_v2 - PhenoAge_NCP_acceleration_v2 | 0.0162522486 | -0.0004944792522 | 0.03285068241 | 0.008837578951 | -0.01160381643 | 0.02892458879 |

The historical comparison uses the read-only defective-v1 analysis pass in
`tables/validation_v2.csv` and `tables/cindex_bootstrap_contrasts.csv`.
Historical submitted PhysioRisk's non-converged HR is not used; the prior
convergence-controlled HR is the scientific comparison value. For explicit
submitted-result provenance, the non-converged value was HR/SD
`2.771657907710413` with C-index `0.6541097324576873`.

## Conclusion robustness

| conclusion_number | conclusion | classification | evidence |
|---|---|---|---|
| 1 | PhysioRisk retains mortality information after age/sex adjustment. | QUALITATIVELY UNCHANGED BUT NUMERICALLY REVISED | PhysioRisk is built from development age/sex-residualized biomarkers; validation HR/SD=1.38493336581, 95% CI 1.33542916001 to 1.43627268685, p=7.72929410744e-69. |
| 2 | PhysioRisk contributes incremental discrimination beyond DemoRisk. | QUALITATIVELY UNCHANGED BUT NUMERICALLY REVISED | Paired delta C=0.0176151332779, 95% CI 0.0119655056227 to 0.0236605267659. |
| 3 | CalibratedTotalRisk has discrimination similar to PhenoAge NCP. | QUALITATIVELY UNCHANGED BUT NUMERICALLY REVISED | Paired delta C=-0.000256849554096, 95% CI -0.00729374931416 to 0.0062613746301. |
| 4 | PhysioRisk numerically exceeds NCP acceleration without established discrimination superiority. | QUALITATIVELY UNCHANGED BUT NUMERICALLY REVISED | Paired delta C=0.00883757895099, 95% CI -0.0116038164324 to 0.0289245887881. |
| 5 | Fixed-horizon calibration remains acceptable. | QUALITATIVELY UNCHANGED BUT NUMERICALLY REVISED | 60m O/E=0.9604, IPCW slope=0.8946; 96m O/E=0.9879, IPCW slope=0.9626 |
| 6 | The PH/time-dependence limitation remains or changes. | QUALITATIVELY UNCHANGED BUT NUMERICALLY REVISED | Schoenfeld p=0.000670474398336; interaction beta=0.129700960167, 95% CI 0.0292947176614 to 0.230107202672, p=0.0113476486457. The Schoenfeld result retains the prespecified p < 0.01 flag; the interaction is diagnostic. |

## Artifacts and safety

All aggregate results are under `outputs/physiorisk_v2_validation/`. The local
participant-level score carrier is ignored by Git:
`outputs/physiorisk_v2_validation/physiorisk_v2_validation_participant_scores.parquet` (SHA256 `b4124a37a07739b18e4583415fe4d7ab14da0e3f1d3fcea101b29c5dfdc451ef`). It is
listed in the artifact manifest, contains 6,739 rows with unique nonmissing
`SEQN`, and contains no new cohort members. Its schema is `SEQN:int64`,
`PERMTH_INT:double`, `MORTSTAT:double`, `RIDAGEYR:double`, `DemoRisk:double`,
`PhysioRisk_2axis_v2:double`, `TotalRisk_original_v2:double`,
`CalibratedTotalRisk_v2:double`, `PhenoAge_NCP_v2:double`, and
`PhenoAge_NCP_acceleration_v2:double`. Commit policy: remain ignored and local;
do not force-add.

No manuscript, supplement, historical table, frozen model output, Research
Square package, GeroScience package, or Biogerontology package was modified.
No manuscript has yet been modified.
