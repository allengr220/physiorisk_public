# Supplementary Material

PhysioRisk: an interpretable survival-modeling framework for separating demographic and physiological mortality risk

Gregory S. Allen

Numerical values are transcribed from the cited canonical artifacts and rounded only for display; source artifacts retain full precision.

\newpage

## Supplementary Table S1. Paired C-index contrasts in the temporal-validation cohort

| Contrast | Cohort | ΔC (A − B) | 95% CI low | 95% CI high | Bootstrap proportion ΔC > 0 | Replicates | Seed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CalibratedTotalRisk − DemoRisk | temporal_test | 0.01628 | 0.01109 | 0.02199 | 1.0 | 2000 | 20260821 |
| CalibratedTotalRisk − PhenoAge NCP | temporal_test | 0.00205 | −0.00326 | 0.00748 | 0.776 | 2000 | 20260821 |
| PhysioRisk − PhenoAge NCP acceleration | temporal_test | 0.01625 | −0.00049 | 0.03285 | 0.97 | 2000 | 20260821 |

Note: Paired percentile intervals were obtained from 2,000 participant bootstrap replicates in the temporal-validation cohort. Contrast estimates and interval limits are shown to the manuscript’s five-decimal reporting precision; the canonical source artifact retains full precision.

Provenance: `tables/cindex_bootstrap_contrasts.csv`.

## Supplementary Table S2. Proportional-hazards diagnostics

| Model | Cohort | N | Deaths | Time transform | Test statistic | P value | Material violation | Flag rule | Cox warning | Scaled-residual region summary |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DemoRisk | temporal_test | 6,739 | 416 | rank | 2.925 | 0.08720586 | False | p<0.01 (prespecified descriptive flag; no multiplicity adjustment) | none | early_0_36m: mean=-0.087; middle_37_72m: mean=0.044; late_73m_plus: mean=0.099 |
| PhysioRisk | temporal_test | 6,739 | 416 | rank | 2.467 | 0.11627106 | False | p<0.01 (prespecified descriptive flag; no multiplicity adjustment) | none | early_0_36m: mean=-0.035; middle_37_72m: mean=0.013; late_73m_plus: mean=0.052 |
| CalibratedTotalRisk | temporal_test | 6,739 | 416 | rank | 16.539 | 0.00004765 | True | p<0.01 (prespecified descriptive flag; no multiplicity adjustment) | none | early_0_36m: mean=-0.177; middle_37_72m: mean=0.108; late_73m_plus: mean=0.161 |
| HematologicStress | temporal_test | 6,739 | 416 | rank | 3.852 | 0.04967436 | False | p<0.01 (prespecified descriptive flag; no multiplicity adjustment) | none |  |
| RenalHepaticTurnover | temporal_test | 6,739 | 416 | rank | 4.304 | 0.03802453 | False | p<0.01 (prespecified descriptive flag; no multiplicity adjustment) | none |  |

Note: The prespecified descriptive flag was p<0.01 without multiplicity adjustment. The regional scaled-residual summaries are reported where present in the canonical artifact.

Provenance: `tables/ph_diagnostics.csv`.

## Supplementary Table S3. Diagnostic log-time interaction analyses

| Model | N | Deaths | Score scale | Time interaction | Reference time (months) | Log HR/SD at 60m | HR/SD at 12m | HR/SD at 60m | HR/SD at 96m | Interaction coefficient | HR multiplier/e-fold time | 95% CI low | 95% CI high | P value | Direction |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DemoRisk | 6,739 | 416 | actual temporal-cohort SD | score_z * log(time_months/60) | 60 | 1.358 | 3.399 | 3.890 | 4.047 | 0.084 | 1.087 | −0.055 | 0.223 | 0.23794 | effect_strengthens_over_time |
| PhysioRisk | 6,739 | 416 | actual temporal-cohort SD | score_z * log(time_months/60) | 60 | 0.356 | 1.366 | 1.428 | 1.446 | 0.027 | 1.028 | −0.032 | 0.087 | 0.36401 | effect_strengthens_over_time |
| CalibratedTotalRisk | 6,739 | 416 | actual temporal-cohort SD | score_z * log(time_months/60) | 60 | 1.320 | 2.842 | 3.744 | 4.057 | 0.171 | 1.187 | 0.066 | 0.277 | 0.00150 | effect_strengthens_over_time |

Note: These analyses are diagnostic only and did not replace or refit the fixed predictors used in temporal validation.

Provenance: `tables/ph_time_interaction.csv`.

## Supplementary Table S4. Fixed-horizon calibration of CalibratedTotalRisk

| Horizon (months) | Training baseline survival | Mean predicted mortality | KM observed mortality | Observed − predicted | O/E ratio | Global Cox slope | Global slope CI low | Global slope CI high | Horizon intercept | Horizon slope | IPCW Brier score | IPCW usable N | No temporal recalibration |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 60 | 0.983687 | 0.046101 | 0.046533 | 0.000432 | 1.009 | 0.811 | 0.762 | 0.859 | −0.101 | 0.941 | 0.03776 | 4,709 | True |
| 96 | 0.966595 | 0.085710 | 0.088256 | 0.002546 | 1.030 | 0.811 | 0.762 | 0.859 | 0.067 | 0.999 | 0.06018 | 1,518 | True |

Note: Absolute risks used the development-derived coefficients and baseline survival. Horizon-specific logistic calibration and Brier scores used temporal-test censoring weights for evaluation only; no temporal recalibration occurred.

Provenance: `tables/calibration_fixed_horizons.csv`.

## Supplementary Table S5. Censoring-robust discrimination diagnostics

| Model | Evaluation cohort | Censoring-distribution cohort | Training N for censoring | Test N | Horizon (months) | Uno C (IPCW) | Cumulative/dynamic AUC (IPCW) | Implementation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DemoRisk | temporal_test | training (1999-2010) | 13,090 | 6,739 | 60 | 0.823 | 0.834 | scikit-survival 0.28.0 |
| DemoRisk | temporal_test | training (1999-2010) | 13,090 | 6,739 | 96 | 0.827 | 0.853 | scikit-survival 0.28.0 |
| PhysioRisk | temporal_test | training (1999-2010) | 13,090 | 6,739 | 60 | 0.654 | 0.657 | scikit-survival 0.28.0 |
| PhysioRisk | temporal_test | training (1999-2010) | 13,090 | 6,739 | 96 | 0.654 | 0.677 | scikit-survival 0.28.0 |
| CalibratedTotalRisk | temporal_test | training (1999-2010) | 13,090 | 6,739 | 60 | 0.839 | 0.850 | scikit-survival 0.28.0 |
| CalibratedTotalRisk | temporal_test | training (1999-2010) | 13,090 | 6,739 | 96 | 0.843 | 0.870 | scikit-survival 0.28.0 |
| PhenoAge NCP | temporal_test | training (1999-2010) | 13,090 | 6,739 | 60 | 0.838 | 0.850 | scikit-survival 0.28.0 |
| PhenoAge NCP | temporal_test | training (1999-2010) | 13,090 | 6,739 | 96 | 0.841 | 0.875 | scikit-survival 0.28.0 |
| PhenoAge NCP acceleration | temporal_test | training (1999-2010) | 13,090 | 6,739 | 60 | 0.641 | 0.655 | scikit-survival 0.28.0 |
| PhenoAge NCP acceleration | temporal_test | training (1999-2010) | 13,090 | 6,739 | 96 | 0.638 | 0.698 | scikit-survival 0.28.0 |

Note: The development cohort estimated the censoring distribution. These were diagnostics of fixed temporal-test predictions, not model-training steps.

Provenance: `tables/censoring_robust_discrimination.csv`.

## Supplementary Table S6. Cycle-specific preselection biomarker missingness and cohort provenance

| Cycle start year | Biomarker | Mortality-eligible N | Missing N | Missing (%) | Denominator population |
| --- | --- | --- | --- | --- | --- |
| 1999 | LBXSAL | 5,445 | 826 | 15.170 | mortality_eligible_before_complete_case_restriction |
| 1999 | LBXSCR | 5,445 | 826 | 15.170 | mortality_eligible_before_complete_case_restriction |
| 1999 | LBXGLU | 5,445 | 3,168 | 58.182 | mortality_eligible_before_complete_case_restriction |
| 1999 | LBXLYPCT | 5,445 | 762 | 13.994 | mortality_eligible_before_complete_case_restriction |
| 1999 | LBXMCV | 5,445 | 732 | 13.444 | mortality_eligible_before_complete_case_restriction |
| 1999 | LBXRDW | 5,445 | 732 | 13.444 | mortality_eligible_before_complete_case_restriction |
| 1999 | LBXSAPSI | 5,445 | 826 | 15.170 | mortality_eligible_before_complete_case_restriction |
| 1999 | LBXWBCSI | 5,445 | 732 | 13.444 | mortality_eligible_before_complete_case_restriction |
| 2001 | LBXSAL | 5,987 | 778 | 12.995 | mortality_eligible_before_complete_case_restriction |
| 2001 | LBXSCR | 5,987 | 778 | 12.995 | mortality_eligible_before_complete_case_restriction |
| 2001 | LBXGLU | 5,987 | 778 | 12.995 | mortality_eligible_before_complete_case_restriction |
| 2001 | LBXLYPCT | 5,987 | 717 | 11.976 | mortality_eligible_before_complete_case_restriction |
| 2001 | LBXMCV | 5,987 | 690 | 11.525 | mortality_eligible_before_complete_case_restriction |
| 2001 | LBXRDW | 5,987 | 690 | 11.525 | mortality_eligible_before_complete_case_restriction |
| 2001 | LBXSAPSI | 5,987 | 778 | 12.995 | mortality_eligible_before_complete_case_restriction |
| 2001 | LBXWBCSI | 5,987 | 690 | 11.525 | mortality_eligible_before_complete_case_restriction |
| 2003 | LBXSAL | 5,610 | 650 | 11.586 | mortality_eligible_before_complete_case_restriction |
| 2003 | LBXSCR | 5,610 | 650 | 11.586 | mortality_eligible_before_complete_case_restriction |
| 2003 | LBXGLU | 5,610 | 650 | 11.586 | mortality_eligible_before_complete_case_restriction |
| 2003 | LBXLYPCT | 5,610 | 591 | 10.535 | mortality_eligible_before_complete_case_restriction |
| 2003 | LBXMCV | 5,610 | 561 | 10.000 | mortality_eligible_before_complete_case_restriction |
| 2003 | LBXRDW | 5,610 | 561 | 10.000 | mortality_eligible_before_complete_case_restriction |
| 2003 | LBXSAPSI | 5,610 | 650 | 11.586 | mortality_eligible_before_complete_case_restriction |
| 2003 | LBXWBCSI | 5,610 | 561 | 10.000 | mortality_eligible_before_complete_case_restriction |
| 2005 | LBXSAL | 5,561 | 586 | 10.538 | mortality_eligible_before_complete_case_restriction |
| 2005 | LBXSCR | 5,561 | 586 | 10.538 | mortality_eligible_before_complete_case_restriction |
| 2005 | LBXGLU | 5,561 | 3,137 | 56.411 | mortality_eligible_before_complete_case_restriction |
| 2005 | LBXLYPCT | 5,561 | 557 | 10.016 | mortality_eligible_before_complete_case_restriction |
| 2005 | LBXMCV | 5,561 | 535 | 9.621 | mortality_eligible_before_complete_case_restriction |
| 2005 | LBXRDW | 5,561 | 535 | 9.621 | mortality_eligible_before_complete_case_restriction |
| 2005 | LBXSAPSI | 5,561 | 586 | 10.538 | mortality_eligible_before_complete_case_restriction |
| 2005 | LBXWBCSI | 5,561 | 535 | 9.621 | mortality_eligible_before_complete_case_restriction |
| 2007 | LBXSAL | 6,219 | 655 | 10.532 | mortality_eligible_before_complete_case_restriction |
| 2007 | LBXSCR | 6,219 | 656 | 10.548 | mortality_eligible_before_complete_case_restriction |
| 2007 | LBXGLU | 6,219 | 3,468 | 55.765 | mortality_eligible_before_complete_case_restriction |
| 2007 | LBXLYPCT | 6,219 | 626 | 10.066 | mortality_eligible_before_complete_case_restriction |
| 2007 | LBXMCV | 6,219 | 612 | 9.841 | mortality_eligible_before_complete_case_restriction |
| 2007 | LBXRDW | 6,219 | 612 | 9.841 | mortality_eligible_before_complete_case_restriction |
| 2007 | LBXSAPSI | 6,219 | 657 | 10.564 | mortality_eligible_before_complete_case_restriction |
| 2007 | LBXWBCSI | 6,219 | 613 | 9.857 | mortality_eligible_before_complete_case_restriction |
| 2009 | LBXSAL | 6,510 | 561 | 8.618 | mortality_eligible_before_complete_case_restriction |
| 2009 | LBXSCR | 6,510 | 561 | 8.618 | mortality_eligible_before_complete_case_restriction |
| 2009 | LBXGLU | 6,510 | 3,581 | 55.008 | mortality_eligible_before_complete_case_restriction |
| 2009 | LBXLYPCT | 6,510 | 500 | 7.680 | mortality_eligible_before_complete_case_restriction |
| 2009 | LBXMCV | 6,510 | 491 | 7.542 | mortality_eligible_before_complete_case_restriction |
| 2009 | LBXRDW | 6,510 | 491 | 7.542 | mortality_eligible_before_complete_case_restriction |
| 2009 | LBXSAPSI | 6,510 | 561 | 8.618 | mortality_eligible_before_complete_case_restriction |
| 2009 | LBXWBCSI | 6,510 | 491 | 7.542 | mortality_eligible_before_complete_case_restriction |
| 2011 | LBXSAL | 5,849 | 700 | 11.968 | mortality_eligible_before_complete_case_restriction |
| 2011 | LBXSCR | 5,849 | 700 | 11.968 | mortality_eligible_before_complete_case_restriction |
| 2011 | LBXGLU | 5,849 | 3,254 | 55.633 | mortality_eligible_before_complete_case_restriction |
| 2011 | LBXLYPCT | 5,849 | 545 | 9.318 | mortality_eligible_before_complete_case_restriction |
| 2011 | LBXMCV | 5,849 | 540 | 9.232 | mortality_eligible_before_complete_case_restriction |
| 2011 | LBXRDW | 5,849 | 540 | 9.232 | mortality_eligible_before_complete_case_restriction |
| 2011 | LBXSAPSI | 5,849 | 702 | 12.002 | mortality_eligible_before_complete_case_restriction |
| 2011 | LBXWBCSI | 5,849 | 540 | 9.232 | mortality_eligible_before_complete_case_restriction |
| 2013 | LBXSAL | 6,100 | 482 | 7.902 | mortality_eligible_before_complete_case_restriction |
| 2013 | LBXSCR | 6,100 | 482 | 7.902 | mortality_eligible_before_complete_case_restriction |
| 2013 | LBXGLU | 6,100 | 3,377 | 55.361 | mortality_eligible_before_complete_case_restriction |
| 2013 | LBXLYPCT | 6,100 | 430 | 7.049 | mortality_eligible_before_complete_case_restriction |
| 2013 | LBXMCV | 6,100 | 414 | 6.787 | mortality_eligible_before_complete_case_restriction |
| 2013 | LBXRDW | 6,100 | 414 | 6.787 | mortality_eligible_before_complete_case_restriction |
| 2013 | LBXSAPSI | 6,100 | 483 | 7.918 | mortality_eligible_before_complete_case_restriction |
| 2013 | LBXWBCSI | 6,100 | 414 | 6.787 | mortality_eligible_before_complete_case_restriction |
| 2015 | LBXSAL | 5,974 | 600 | 10.044 | mortality_eligible_before_complete_case_restriction |
| 2015 | LBXSCR | 5,974 | 601 | 10.060 | mortality_eligible_before_complete_case_restriction |
| 2015 | LBXGLU | 5,974 | 3,406 | 57.014 | mortality_eligible_before_complete_case_restriction |
| 2015 | LBXLYPCT | 5,974 | 564 | 9.441 | mortality_eligible_before_complete_case_restriction |
| 2015 | LBXMCV | 5,974 | 563 | 9.424 | mortality_eligible_before_complete_case_restriction |
| 2015 | LBXRDW | 5,974 | 563 | 9.424 | mortality_eligible_before_complete_case_restriction |
| 2015 | LBXSAPSI | 5,974 | 601 | 10.060 | mortality_eligible_before_complete_case_restriction |
| 2015 | LBXWBCSI | 5,974 | 563 | 9.424 | mortality_eligible_before_complete_case_restriction |

Note: Missingness was quantified within each cycle among mortality-eligible participants before complete-case restriction. The denominator is repeated for each biomarker within a cycle; biomarker-specific missing counts are not joint complete-case exclusions.

Provenance: `tables/missingness_by_cycle.csv`.

## Supplementary Table S7. Mortality-eligible participants included in versus excluded from the benchmark cohort

| Group | Population definition | N | Age mean | Age SD | Female (%) | Deaths N | Deaths (%) | Median follow-up (months) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| benchmark_included | Complete for notebook 01 EXTENDED_16 | 19,829 | 47.009 | 19.050 | 50.643 | 2,936 | 14.807 | 124 |
| excluded_before_benchmark | Missing one or more notebook 01 EXTENDED_16 fields | 33,426 | 47.784 | 19.862 | 52.486 | 6,168 | 18.453 | 122 |

Note: Inclusion was defined by completeness for notebook 01’s EXTENDED_16 fields. The two groups partition the 53,255 mortality-eligible participants: 19,829 included and 33,426 excluded.

Provenance: `tables/cohort_included_excluded_characteristics.csv`.

## Supplementary Table S8. Common complete-case and training-derived-imputation sensitivity analyses

| Analysis | Score | Cohort | N | Deaths | C-index | Age correlation | Missing-data rule | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| common_complete_case | PhysioRisk | temporal_test | 6,739 | 416 | 0.654 | 0.106 | identical participants; all no-CRP comparator and PhysioRisk biomarkers observed | performed |
| common_complete_case | PhenoAge NCP (no-CRP proxy) | temporal_test | 6,739 | 416 | 0.841 | 0.961 | identical participants; all no-CRP comparator and PhysioRisk biomarkers observed | performed |
| common_training_derived_imputation | PhysioRisk | temporal_test | 6,739 | 416 | 0.654 | 0.106 | no-op in retained benchmark because all required biomarkers are observed; upstream imputation cannot be reconstructed | performed as degenerate no-missing sensitivity; extension to excluded source participants not estimable without frozen residualization parameters |
| common_training_derived_imputation | PhenoAge NCP (no-CRP proxy) | temporal_test | 6,739 | 416 | 0.841 | 0.961 | no-op in retained benchmark because all required biomarkers are observed; upstream imputation cannot be reconstructed | performed as degenerate no-missing sensitivity; extension to excluded source participants not estimable without frozen residualization parameters |

Note: All 6,739 temporal-validation participants in the retained benchmark already had the biomarkers required for both scores. Common training-derived imputation was therefore a no-op and changed no observations; extension to excluded source participants was not estimable from the frozen retained scoring path.

Provenance: `tables/comparator_sensitivity.csv`.

## Supplementary Table S9. Historical submitted benchmark results retained for provenance only

| Status | Interpretation | Cohort | Risk score | C-index | HR per 1 SD | HR CI low | HR CI high | P value | Age correlation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| historical_submitted_not_current | provenance_only; PhysioRisk HR did not converge and TotalRisk_2axis is the obsolete unit-weight composite | test_benchmark | BaselineRisk | 0.827 | 3.736 | 3.347 | 4.170 | 4.38e-122 | 0.970 |
| historical_submitted_not_current | provenance_only; PhysioRisk HR did not converge and TotalRisk_2axis is the obsolete unit-weight composite | test_benchmark | PhysioRisk_2axis | 0.654 | 2.772 | 2.656 | 2.893 | 0 | 0.106 |
| historical_submitted_not_current | provenance_only; PhysioRisk HR did not converge and TotalRisk_2axis is the obsolete unit-weight composite | test_benchmark | TotalRisk_2axis | 0.840 | 1.877 | 1.815 | 1.942 | 1.08e-293 | 0.811 |
| historical_submitted_not_current | provenance_only; PhysioRisk HR did not converge and TotalRisk_2axis is the obsolete unit-weight composite | test_benchmark | PhenoAge_noCRP_proxy | 0.841 | 3.976 | 3.637 | 4.347 | 3.4e-202 | 0.961 |
| historical_submitted_not_current | provenance_only; PhysioRisk HR did not converge and TotalRisk_2axis is the obsolete unit-weight composite | test_benchmark | PhenoAgeAccel | 0.638 | 1.432 | 1.360 | 1.508 | 3.7e-42 | 0.033 |
| historical_submitted_not_current | provenance_only; PhysioRisk HR did not converge and TotalRisk_2axis is the obsolete unit-weight composite | train_benchmark | BaselineRisk | 0.855 | 4.286 | 4.097 | 4.484 | 0 | 0.971 |
| historical_submitted_not_current | provenance_only; PhysioRisk HR did not converge and TotalRisk_2axis is the obsolete unit-weight composite | train_benchmark | PhysioRisk_2axis | 0.602 | 1.334 | 1.295 | 1.374 | 1.07e-81 | −0.000 |
| historical_submitted_not_current | provenance_only; PhysioRisk HR did not converge and TotalRisk_2axis is the obsolete unit-weight composite | train_benchmark | TotalRisk_2axis | 0.858 | 2.427 | 2.372 | 2.483 | 0 | 0.790 |
| historical_submitted_not_current | provenance_only; PhysioRisk HR did not converge and TotalRisk_2axis is the obsolete unit-weight composite | train_benchmark | PhenoAge_noCRP_proxy | 0.864 | 3.670 | 3.556 | 3.787 | 0 | 0.958 |
| historical_submitted_not_current | provenance_only; PhysioRisk HR did not converge and TotalRisk_2axis is the obsolete unit-weight composite | train_benchmark | PhenoAgeAccel | 0.586 | 1.246 | 1.219 | 1.274 | 1.13e-85 | 0.000 |

Note: Historical provenance only. The historical PhysioRisk hazard-ratio fit did not converge, and TotalRisk_2axis is the obsolete unit-weight composite. These rows are not current manuscript results.

Provenance: `manuscript/generated/table_s9_historical_submitted_results.csv` (generated by `scripts/build_s4_manuscript_assets.py` from `tables/physiorisk_vs_phenoage_aligned_comparison.csv`).
