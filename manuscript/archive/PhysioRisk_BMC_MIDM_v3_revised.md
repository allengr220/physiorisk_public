# PhysioRisk: an interpretable survival-modeling framework for separating demographic and physiological mortality risk

Gregory S. Allen

Independent researcher, Cuenca, Ecuador

## Abstract

**Background:** Biomarker-based mortality scores often combine chronological age with physiological measurements, obscuring whether predicted risk reflects demographic mortality structure or physiological deviation. We asked whether mortality risk could be decomposed into a demographic component and an age- and sex-adjusted physiological component while preserving useful prognostic information.

**Methods:** We analyzed unweighted, mortality-linked NHANES 1999–2016 data. DemoRisk was an age- and sex-based Cox linear predictor trained in 1999–2010. PhysioRisk was derived from development-residualized biomarkers summarized in two physiological axes and applied unchanged in temporal validation. CalibratedTotalRisk recombined the fixed components using coefficients estimated only in development (1.0586578128×DemoRisk + 0.3563514639×PhysioRisk). The documented scoring path and CalibratedTotalRisk coefficients were fixed before internal temporal validation in 2011–2016. We evaluated hazard ratios (HRs) per validation-cohort standard deviation, Harrell C-index with 2,000 participant bootstrap replicates, paired C-index contrasts, proportional-hazards diagnostics, 5- and 8-year calibration and inverse-probability-of-censoring-weighted (IPCW) Brier scores, and censoring-robust discrimination. PhenoAge NCP was a no-CRP proxy rather than the full PhenoAge implementation.

**Results:** Of 92,062 source-cycle participants, 53,255 were mortality eligible and 19,829 formed the biomarker-complete cohort; 13,090 participants (2,520 deaths) were used for development and 6,739 (416 deaths) for temporal validation. PhysioRisk had low age correlation (r=0.106), C-index 0.654 (95% CI 0.624–0.685), and HR 1.387 (95% CI 1.338–1.439). CalibratedTotalRisk had C-index 0.843 (95% CI 0.822–0.863), exceeding DemoRisk by 0.016 (paired 95% CI 0.011–0.022). Its difference from PhenoAge NCP was 0.002 (paired 95% CI −0.003 to 0.007), providing no evidence of a discrimination difference. Five- and 8-year mean predicted mortality closely matched Kaplan–Meier observed mortality (4.610% vs 4.653% and 8.571% vs 8.826%); horizon-specific slopes were 0.941 and 0.999. CalibratedTotalRisk violated strict proportional hazards, with its association strengthening over follow-up.

**Conclusions:** Age- and sex-adjusted physiology retained mortality information and improved discrimination when recombined with demographic risk. Comparable discrimination with PhenoAge NCP shows that explicit demographic–physiological decomposition can preserve useful risk ranking; it does not establish superiority. Findings are from an unweighted complete-case analytic cohort with internal temporal validation, and external validation remains necessary.

**Keywords:** mortality prediction; survival analysis; Cox proportional hazards; interpretability; biomarker modeling; NHANES; prognostic models; risk decomposition

## Introduction

All-cause mortality models commonly combine chronological age and clinical biomarkers in a single score. This can produce strong risk ranking, but it makes the source of that ranking difficult to interpret: demographic mortality structure and physiological deviation are entangled. The distinction is particularly important when mortality-trained scores are discussed as measures of biological or physiological aging [1–3].

PhenoAge directly optimized mortality prediction using clinical biomarkers and age [4]. Other work on physiological dysregulation has emphasized multisystem statistical distance from a reference state [5–7], while frailty research characterizes heterogeneity through latent vulnerability or accumulated deficits [8–10]. These perspectives provide complementary descriptions of aging-related risk.

PhysioRisk differs conceptually from mortality-trained biological-age scores, physiological-dysregulation distances, and age-acceleration residuals. It explicitly constructs separate demographic and physiological mortality-risk components and permits their training-calibrated recombination while retaining both components as interpretable objects. This is a modeling distinction rather than a claim that the components constitute biological age or that the framework is superior to established scores.

The central research question was whether mortality risk could be decomposed into a demographic component and an age- and sex-adjusted physiological component while preserving useful prognostic information. DemoRisk captures risk associated with age and sex. PhysioRisk summarizes mortality-associated deviations of biomarkers from age- and sex-expected values. A development-calibrated recombination permits overall risk ranking without abandoning the separate interpretation of its components.

We evaluated whether PhysioRisk retained mortality information after residualization, whether it added discrimination beyond DemoRisk, whether calibrated recombination preserved discrimination relative to a PhenoAge no-CRP proxy, and whether temporal performance was supported by uncertainty, calibration, proportional-hazards, and censoring-robust diagnostics. Reporting was guided by TRIPOD [11].

## Methods

### Study population, mortality linkage, and temporal split

Data came from nine continuous NHANES cycles from 1999–2000 through 2015–2016 [12]. The source-cycle union contained 92,062 participants. Records were linked one-to-one by participant identifier to the 2019 public-use linked mortality files [13]. Mortality eligibility required ELIGSTAT=1 and nonmissing follow-up time (PERMTH_INT) and mortality status (MORTSTAT), yielding 53,255 participants and 9,104 deaths. The endpoint was all-cause mortality. Follow-up began at the NHANES examination and ended at death or administrative censoring as recorded in PERMTH_INT; participants without a recorded death were censored at their recorded follow-up month.

Complete data for the variables required by the prespecified biomarker construction were available for 19,829 participants (2,936 deaths). The downstream eight-biomarker no-CRP comparison removed no additional participants. Earlier cycles (1999–2000 through 2009–2010) formed the development cohort (n=13,090; 2,520 deaths). Later cycles (2011–2012 through 2015–2016) formed the internal temporal-validation cohort (n=6,739; 416 deaths) (Figure 1 and Table 1).

NHANES uses a national probability sampling design, but analyses were unweighted because the objective was prediction-model development and temporal evaluation rather than population estimation. Estimates therefore describe this selected analytic cohort and are not population-representative NHANES estimates.

### Missing data and cohort selection

For each cycle, missingness in the eight unique biomarkers required by PhysioRisk or PhenoAge NCP was quantified among mortality-eligible participants before complete-case restriction. Participants in the analytic cohort were compared descriptively with the 33,426 mortality-eligible participants excluded for missing one or more required fields. These comparisons summarized age, sex, deaths, and follow-up and did not modify the model specification (Supplementary Tables S6 and S7).

All five scores were evaluated in the same 6,739 complete temporal-validation participants. Training-median imputation for the PhenoAge NCP implementation consequently changed no values in this cohort. Common complete-case and common training-derived-imputation sensitivity analyses were recorded; extension to excluded participants was not attempted because the exact physiological residualization parameters needed to score them were unavailable (Supplementary Table S8).

### DemoRisk

DemoRisk was the log partial-hazard prediction from a Cox proportional hazards model [14,15] containing natural cubic spline terms for age (four degrees of freedom) and sex, with an L2 penalizer of 0.01. The model and spline design were fitted only in the 1999–2010 development cohort and applied unchanged to 2011–2016.

### PhysioRisk

Each biomarker was regressed on natural cubic spline terms for age and sex in the development cohort. The fitted regression functions were applied to temporal-validation observations, and residuals were standardized using development-cohort means and standard deviations. HematologicStress was the signed average of standardized residuals for white blood cell count, lymphocyte percentage (reversed), mean corpuscular volume, and red cell distribution width. RenalHepaticTurnover similarly combined creatinine, albumin (reversed), and alkaline phosphatase.

The preserved final scoring and evaluation path contains a fixed two-axis score applied unchanged in temporal validation; the earlier sequence of decisions leading to selection of the two axes is incompletely reconstructed and is not asserted to have been entirely development-only. The raw linear predictor used coefficients 0.433×HematologicStress + 0.235×RenalHepaticTurnover; the displayed coefficients are rounded. PhysioRisk was this raw predictor standardized using development-cohort parameters. Within the preserved final path, residualization functions, axis definitions, score coefficients, and standardization parameters were not refitted in temporal validation. Cox inference for PhysioRisk used a convergence-controlled fit and expressed the HR per one observed standard deviation in the temporal-validation cohort.

### Calibrated total risk

The primary composite was defined as:

CalibratedTotalRisk = 1.0586578127615558×DemoRisk + 0.3563514638575306×PhysioRisk.

Both coefficients were estimated jointly in an unpenalized Cox model [14,15] using only the development cohort and were then fixed for temporal validation. Neither coefficient was selected using temporal-validation performance. DemoRisk and PhysioRisk were also retained and evaluated separately.

### Comparator

PhenoAge NCP was constructed from the published PhenoAge biomarker coefficients [4] with C-reactive protein omitted in the locked analysis pipeline. It is therefore a PhenoAge no-CRP proxy, not the complete published implementation. PhenoAge NCP acceleration was the residual from a regression of PhenoAge NCP on spline-transformed age and sex fitted in development and applied unchanged to temporal validation.

### Validation and statistical analysis

Known limitations of concordance measures for censored survival outcomes informed interpretation [16]. Kaplan–Meier estimation was used for observed risks and censoring distributions [17].

All five primary scores were evaluated in the same temporal-validation cohort. Harrell C-index quantified rank discrimination [18]. Participant-level bootstrap resampling with 2,000 replicates (seed 20260821) provided percentile 95% confidence intervals for each C-index and paired confidence intervals for prespecified C-index contrasts. Cox HRs and 95% confidence intervals were estimated after division by each score's temporal-cohort sample standard deviation; fits were checked for convergence. Pearson correlation summarized association with chronological age.

The proportional-hazards assumption was evaluated with rank-time Schoenfeld tests and scaled Schoenfeld residuals [19]. A prespecified descriptive flag used p<0.01 without multiplicity adjustment. Separate diagnostic extended Cox models included standardized score × log(time/60 months) interactions as related time-varying-effect diagnostics [19]. These temporal-cohort fits assessed time variation only and neither replaced nor recalibrated the development-derived prediction model.

Absolute mortality probabilities at 5 and 8 years were calculated from the development-cohort Cox coefficients and baseline survival. Calibration assessment followed established prognostic-model principles [20,21] and included mean predicted risk, Kaplan–Meier observed risk, observed-to-expected ratio, a global Cox calibration slope, decile calibration plots, and horizon-specific logistic calibration. For a horizon t, the binary outcome indicated death by t. Participants with known status at t contributed directly; those censored before t were weighted using inverse probabilities from the temporal-validation censoring Kaplan–Meier estimate [22]. A weighted logistic regression of the binary outcome on the logit of the fixed predicted risk, using those censoring weights, estimated the calibration intercept and slope. The same IPCW scheme was used for the Brier score at each horizon [22]. These references support the general survival-calibration and censoring-adjustment principles rather than defining this exact implementation. Temporal outcomes supplied evaluation weights and outcomes only; prediction coefficients and baseline survival remained development-derived, and no temporal recalibration occurred.

As censoring-robust discrimination checks, Uno IPCW C truncated at 5 and 8 years [23] and cumulative/dynamic AUC [24] were calculated using the development cohort to estimate the censoring distribution. Follow-up support was summarized with reverse Kaplan–Meier follow-up and numbers at risk. These analyses were diagnostics of the fixed predictions rather than model-training steps.

## Results

### Cohort construction and selection

The cohort flow was 92,062 source-cycle participants, 53,255 mortality-eligible participants (9,104 deaths), and 19,829 biomarker-complete participants (2,936 deaths). The analytic cohort split into 13,090 development participants (2,520 deaths) and 6,739 temporal-validation participants (416 deaths) (Figure 1 and Table 1).

Among mortality-eligible participants, included participants had mean age 47.009 years (SD 19.050), were 50.643% female, had 2,936 deaths (14.807%), and had median follow-up of 124 months. The 33,426 excluded participants had mean age 47.784 years (SD 19.862), were 52.486% female, had 6,168 deaths (18.453%), and had median follow-up of 122 months. Complete-case selection therefore retained a group with a lower observed death proportion, limiting generalization beyond the analytic cohort (Supplementary Table S7).

Temporal-validation reverse Kaplan–Meier median follow-up was 74 months. There were 4,461 participants at risk at 5 years and 1,137 at 8 years; the 8-year evaluation was supported but had a less precise tail.

### Discrimination, mortality association, and age correlation

DemoRisk had C-index 0.827 (bootstrap 95% CI 0.804–0.847), HR 3.736 per temporal-cohort SD (95% CI 3.347–4.170), and age correlation 0.970 (Table 2). PhysioRisk had C-index 0.654 (95% CI 0.624–0.685), low age correlation (r=0.106), and HR 1.387 (95% CI 1.338–1.439), showing that age- and sex-adjusted physiological variation retained mortality information.

CalibratedTotalRisk had C-index 0.843 (95% CI 0.822–0.863), HR 3.259 (95% CI 3.036–3.498), and age correlation 0.946. It exceeded DemoRisk by ΔC=0.01628 (paired 95% CI 0.01109–0.02199), supporting incremental discrimination from the physiological component.

PhenoAge NCP had C-index 0.841 (95% CI 0.819–0.861), HR 3.976 (95% CI 3.637–4.347), and age correlation 0.961. The difference between CalibratedTotalRisk and PhenoAge NCP was ΔC=0.00205 (paired 95% CI −0.00326 to 0.00748); no discrimination difference was established. The comparable performance supports preservation of useful risk ranking by the decomposed architecture, not superiority over PhenoAge NCP.

PhenoAge NCP acceleration had C-index 0.638 (95% CI 0.606–0.668), HR 1.432 (95% CI 1.360–1.508), and age correlation 0.033. PhysioRisk exceeded its C-index by 0.01625, but the paired 95% CI included zero (−0.00049 to 0.03285). The difference was suggestive rather than conclusive.

### Fixed-horizon calibration

At 5 years, mean predicted mortality from CalibratedTotalRisk was 4.610% and Kaplan–Meier observed mortality was 4.653% (observed minus predicted 0.043 percentage points; O/E 1.009). At 8 years, the corresponding values were 8.571% and 8.826% (difference 0.255 percentage points; O/E 1.030). Horizon-specific calibration slopes were 0.941 and 0.999, with intercepts −0.101 and 0.067 (Figure 2). These estimates had no bootstrap confidence intervals. IPCW Brier scores were 0.03776 at 5 years and 0.06018 at 8 years.

The global Cox calibration slope was 0.811 (95% CI 0.762–0.859). Because this summary assumes a constant score effect, it cannot be interpreted simply as overfitting in the presence of the time-varying association reported below.

### Proportional-hazards diagnostics

CalibratedTotalRisk violated the strict proportional-hazards assumption (rank-time Schoenfeld statistic 16.539, p=4.76×10⁻⁵). Mean scaled residuals changed from −0.177 at 0–36 months to 0.108 at 37–72 months and 0.161 thereafter. A diagnostic score × log-time model gave interaction coefficient 0.171 (95% CI 0.066–0.277; p=0.00150), consistent with an association that strengthened over follow-up. This diagnostic model did not replace the fixed predictor.

DemoRisk (p=0.087) and PhysioRisk (p=0.116) did not show comparable material violations. Their diagnostic log-time interactions were smaller and nonsignificant: 0.084 (p=0.238) for DemoRisk and 0.027 (p=0.364) for PhysioRisk.

### Censoring-robust and missing-data sensitivity analyses

At 5 and 8 years, Uno C was 0.839 and 0.843 for CalibratedTotalRisk, 0.823 and 0.827 for DemoRisk, and 0.838 and 0.841 for PhenoAge NCP. Corresponding cumulative/dynamic AUCs were 0.850 and 0.870, 0.834 and 0.853, and 0.850 and 0.875. PhysioRisk Uno C was 0.654 at both horizons. These censoring-robust metrics preserved the conclusions from Harrell C-index.

All 6,739 temporal-validation participants had the biomarkers required for both primary scores. Common complete-case analysis therefore reproduced PhysioRisk and PhenoAge NCP C-indices of 0.654 and 0.841, and common training-derived imputation changed no observations. Cycle-specific preselection missingness and the included/excluded comparison are reported in Supplementary Tables S6–S8.

## Discussion

### Principal findings

Age- and sex-adjusted physiological variation retained mortality information in internal temporal validation. Although PhysioRisk alone had modest discrimination, it had low correlation with age and contributed information beyond DemoRisk: development-calibrated recombination improved C-index by 0.01628, with a paired interval excluding zero. CalibratedTotalRisk and PhenoAge NCP had comparable discrimination, with no established difference in either direction. The main contribution is therefore interpretable separation and recombination of demographic and physiological risk, not predictive superiority.

These results show that much of overall mortality discrimination resides in demographic structure while residualized clinical physiology supplies complementary information. PhysioRisk does not establish biological age or causal independence from aging; it is a mortality-associated summary of biomarker deviations conditional on measured age and sex. Its low age correlation confirms statistical residualization, not a biological mechanism.

Jointly estimating the two CalibratedTotalRisk recombination coefficients in development produced a coherent composite while preserving component interpretation. The paired improvement over DemoRisk supports added prognostic information; those recombination coefficients were estimated without temporal-performance model selection.

CalibratedTotalRisk's discrimination was statistically indistinguishable from the no-CRP proxy. This comparable performance suggests that separating demographic and physiological components need not sacrifice useful mortality ranking. It does not establish superiority over PhenoAge, and the comparator was not the complete PhenoAge implementation. The physiology-only C-index contrast favored PhysioRisk over PhenoAge NCP acceleration, but its interval crossed zero and should be viewed as suggestive.

Mean predicted and observed risks were close and horizon-specific slopes were near one at both 5 and 8 years. These findings characterize fixed-horizon calibration in this temporal cohort; they do not establish transportability to other populations. The 8-year tail had fewer participants at risk, and horizon-specific slope estimates lacked bootstrap confidence intervals. The global Cox calibration slope of 0.811 summarizes a different model assumption and should not be reduced to an overfitting label.

CalibratedTotalRisk failed strict proportional hazards, and its association strengthened over follow-up. The violation does not negate the observed discrimination or fixed-horizon calibration in this temporal cohort. It does limit interpretation of a single constant CalibratedTotalRisk hazard ratio. The log-time interaction was a temporal-cohort diagnostic and was not used to alter the prediction model.

### Limitations

This study used internal temporal validation across NHANES cycles, not external validation. Independent cohorts are required to assess transportability and clinical utility. NHANES uses a national sampling design, but these analyses were unweighted and restricted to a complete-case analytic cohort. The 33,426 mortality-eligible participants excluded before analysis had a higher observed death proportion than included participants, and biomarker missingness varied by cycle. These selection features constrain generalizability and preclude population-representative interpretation.

The comparator omitted CRP and is a PhenoAge no-CRP proxy rather than the complete published implementation. Common missing-data sensitivities were uninformative within the retained cohort because all required comparator biomarkers were observed. Scoring excluded participants would require physiological residualization and axis parameters that were unavailable and was not attempted.

The two physiological axes are transparent summaries, not definitive biological systems or causal mechanisms. The displayed raw-score coefficients 0.433 and 0.235 are rounded. Calibration-slope uncertainty was not estimated at each fixed horizon, subgroup performance and clinical decision utility were not evaluated, and the 8-year calibration tail was less precise.

### Conclusions

Mortality risk could be separated into a dominant demographic component and a low-age-correlation physiological component while retaining useful prognostic performance. Physiology added discrimination beyond DemoRisk, and development-calibrated recombination performed comparably to PhenoAge NCP. This supports decomposition as an interpretable modeling strategy; external validation and broader missing-data and transportability assessments remain necessary.

## Declarations

### Ethics approval and consent to participate

This study used publicly available, de-identified NHANES data and public-use linked mortality files. NHANES protocols were approved by the NCHS Research Ethics Review Board, and participants provided informed consent. This secondary analysis did not require additional institutional review board approval.

### Consent for publication

Not applicable.

### Data and code availability

NHANES data and public-use linked mortality files are publicly available from the National Center for Health Statistics [12,13]. Analysis code, aggregate tables, and reproducibility documentation accompany this article. Participant-level derived data are not distributed.

### Competing interests

The author declares no competing interests.

### Funding

No external funding was received.

### Author contributions

GSA conceived the study, developed the modeling framework, conducted the analyses, interpreted the results, and wrote the manuscript.

## Tables and figures

**Table 1. Characteristics of the development and temporal-validation cohorts.** Statistics were regenerated descriptively from the SHA256-locked scored participant-level parquets. Percentages use cohort size as the denominator; follow-up is reported in months. Detailed source-cycle counts and the mortality-eligible included/excluded comparison are provided in Supplementary Tables S6 and S7.

**Table 2. Model performance in the temporal-validation cohort.** All models were evaluated in 6,739 participants with 416 deaths. C-index intervals are percentile intervals from 2,000 participant bootstrap replicates. Hazard ratios are per temporal-validation-cohort standard deviation. Paired intervals for direct C-index contrasts are reported in the Results and Supplementary Table S1.

**Figure 1. Cohort flow.** Flow of NHANES 1999–2016 participants from the source-cycle population through mortality eligibility and biomarker completeness to the development and internal temporal-validation cohorts. Counts of deaths are reported in the text and Table 1.

**Figure 2. Fixed-horizon calibration of CalibratedTotalRisk in temporal validation.** Mean predicted mortality and Kaplan–Meier observed mortality are shown by risk decile at 5 and 8 years. The dashed diagonal denotes perfect agreement.

## References

1. Lu AT, Quach A, Wilson JG, Reiner AP, Aviv A, Raj K, et al. DNA methylation GrimAge strongly predicts lifespan and healthspan. Aging (Albany NY). 2019;11(2):303–327. https://doi.org/10.18632/aging.101684
2. Ferrucci L, Levine ME, Kuo PL, Simonsick EM. Time and the metrics of aging. Circulation Research. 2018;123(7):740–744. https://doi.org/10.1161/CIRCRESAHA.118.312816
3. Klemera P, Doubal S. A new approach to the concept and computation of biological age. Mech Ageing Dev. 2006;127(3):240–248. https://doi.org/10.1016/j.mad.2005.10.004
4. Liu Z, Kuo PL, Horvath S, Crimmins E, Ferrucci L, Levine M. A new aging measure captures morbidity and mortality risk across diverse subpopulations from NHANES IV: a cohort study. PLoS Med. 2018;15(12):e1002718. https://doi.org/10.1371/journal.pmed.1002718
5. Cohen AA, Milot E, Li Q, et al. A novel statistical approach shows evidence for multi-system physiological dysregulation during aging. Mech Ageing Dev. 2013;134(3–4):110–117. https://doi.org/10.1016/j.mad.2013.01.004
6. Milot E, Cohen AA, Li Q, et al. Relationships between physiological dysregulation and health outcomes in aging: trajectories and mortality associations. Mech Ageing Dev. 2014;141–142:7–16. https://doi.org/10.1016/j.mad.2014.10.001
7. Cohen AA, Li Q, Milot E, et al. Statistical distance as a measure of physiological dysregulation is largely robust to variation in its biomarker composition. PLoS One. 2015;10(4):e0122541. https://doi.org/10.1371/journal.pone.0122541
8. Vaupel JW, Manton KG, Stallard E. The impact of heterogeneity in individual frailty on the dynamics of mortality. Demography. 1979;16(3):439–454. https://doi.org/10.2307/2061224
9. Duchateau L, Janssen P. The Frailty Model. New York: Springer; 2007. https://doi.org/10.1007/978-0-387-72835-3
10. Rockwood K, Mitnitski A. Frailty in relation to the accumulation of deficits. J Gerontol A Biol Sci Med Sci. 2007;62(7):722–727. https://doi.org/10.1093/gerona/62.7.722
11. Collins GS, Reitsma JB, Altman DG, Moons KGM. Transparent reporting of a multivariable prediction model for individual prognosis or diagnosis: the TRIPOD statement. Ann Intern Med. 2015;162(1):55–63. https://doi.org/10.7326/M14-0697
12. National Center for Health Statistics. National Health and Nutrition Examination Survey Data. Hyattsville, MD: Centers for Disease Control and Prevention; 1999–2016. Available from: https://www.cdc.gov/nchs/nhanes/
13. National Center for Health Statistics. National Health and Nutrition Examination Survey: public-use linked mortality file description. Hyattsville, MD: Centers for Disease Control and Prevention. Available from: https://www.cdc.gov/nchs/data/datalinkage/public-use-linked-mortality-file-description.pdf
14. Cox DR. Regression models and life-tables. J R Stat Soc Series B Stat Methodol. 1972;34(2):187–220. https://doi.org/10.1111/j.2517-6161.1972.tb00899.x
15. Kleinbaum DG, Klein M. Survival Analysis: A Self-Learning Text. 3rd ed. New York: Springer; 2012. https://doi.org/10.1007/978-1-4419-6646-9
16. Hartman N, Kim S, He K, Kalbfleisch JD. Pitfalls of the concordance index for survival outcomes. Stat Med. 2023;42(13):2179–2190. https://doi.org/10.1002/sim.9717
17. Bewick V, Cheek L, Ball J. Statistics review 12: survival analysis. Crit Care. 2004;8(5):389–394. https://doi.org/10.1186/cc2955
18. Harrell FE Jr, Lee KL, Mark DB. Multivariable prognostic models: issues in developing models, evaluating assumptions and adequacy, and measuring and reducing errors. Stat Med. 1996;15(4):361–387. https://doi.org/10.1002/(SICI)1097-0258(19960229)15:4<361::AID-SIM168>3.0.CO;2-4
19. Grambsch PM, Therneau TM. Proportional hazards tests and diagnostics based on weighted residuals. Biometrika. 1994;81(3):515–526. https://doi.org/10.1093/biomet/81.3.515
20. Crowson CS, Atkinson EJ, Therneau TM. Assessing calibration of prognostic risk scores. Stat Methods Med Res. 2016;25(4):1692–1706. https://doi.org/10.1177/0962280213497434
21. Royston P. Tools for checking calibration of a Cox model in external validation: approach based on individual event probabilities. Stata J. 2014;14(4):738–755. https://doi.org/10.1177/1536867X1401400403
22. Graf E, Schmoor C, Sauerbrei W, Schumacher M. Assessment and comparison of prognostic classification schemes for survival data. Stat Med. 1999;18(17–18):2529–2545. https://doi.org/10.1002/(SICI)1097-0258(19990915/30)18:17/18<2529::AID-SIM274>3.0.CO;2-5
23. Uno H, Cai T, Pencina MJ, D'Agostino RB, Wei LJ. On the C-statistics for evaluating overall adequacy of risk prediction procedures with censored survival data. Stat Med. 2011;30(10):1105–1117. https://doi.org/10.1002/sim.4154
24. Heagerty PJ, Lumley T, Pepe MS. Time-dependent ROC curves for censored survival data and a diagnostic marker. Biometrics. 2000;56(2):337–344. https://doi.org/10.1111/j.0006-341X.2000.00337.x
