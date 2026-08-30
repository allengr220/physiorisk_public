# Sprint 4 manuscript change map

## Scope and governing rule

This audit precedes all Sprint 4 manuscript edits. The canonical evidence is the newest revision/provenance documentation and generated CSV output from the frozen Sprint 1, Sprint 2, and Sprint 3D analyses. Historical submitted results remain valid only when explicitly labeled as historical; they are not current manuscript results.

## Canonical results for revised numerical claims

| Claim | Exact value | Canonical source |
|---|---:|---|
| Source-cycle participants | 92,062 | `tables/cohort_flow.csv` |
| Mortality eligible / deaths | 53,255 / 9,104 | `tables/cohort_flow.csv` |
| Biomarker-complete benchmark / deaths | 19,829 / 2,936 | `tables/cohort_flow.csv` |
| Training / deaths | 13,090 / 2,520 | `tables/cohort_flow.csv` |
| Temporal validation / deaths | 6,739 / 416 | `tables/cohort_flow.csv` |
| Included age, female, deaths, median follow-up | 47.009 (SD 19.050); 50.643%; 2,936 (14.807%); 124 months | `tables/cohort_included_excluded_characteristics.csv` |
| Excluded age, female, deaths, median follow-up | 47.784 (SD 19.862); 52.486%; 6,168 (18.453%); 122 months | `tables/cohort_included_excluded_characteristics.csv` |
| CalibratedTotalRisk coefficients | beta_Demo=1.0586578127615558; beta_Physio=0.3563514638575306 | `tables/totalrisk_training_coefficients.csv` |
| DemoRisk C / bootstrap 95% CI; HR/SD; age r | 0.8268759556 (0.8040182995–0.8469372226); 3.7356739803 (3.3467691320–4.1697707660); 0.9697340218 | `tables/validation_v2.csv` |
| PhysioRisk corrected C / bootstrap 95% CI; HR/SD; age r | 0.6541097325 (0.6242830616–0.6850265972); 1.3874682647 (1.3375161943–1.4392858895); 0.1062334525 | `tables/validation_v2.csv` |
| CalibratedTotalRisk C / bootstrap 95% CI; HR/SD; age r | 0.8431533308 (0.8217959357–0.8627076570); 3.2590016242 (3.0359971144–3.4983865882); 0.9464909892 | `tables/validation_v2.csv` |
| PhenoAge NCP C / bootstrap 95% CI; HR/SD; age r | 0.8411083058 (0.8191165115–0.8610201835); 3.9761162023 (3.6369226850–4.3469442227); 0.9613694861 | `tables/validation_v2.csv` |
| PhenoAge NCP acceleration C / bootstrap 95% CI; HR/SD; age r | 0.6378574839 (0.6058761163–0.6679426474); 1.4321474553 (1.3599315530–1.5081982098); 0.0332988754 | `tables/validation_v2.csv` |
| CalibratedTotalRisk − DemoRisk C | 0.0162773752 (paired bootstrap 95% CI 0.0110921647–0.0219872027) | `tables/cindex_bootstrap_contrasts.csv` |
| CalibratedTotalRisk − PhenoAge NCP C | 0.0020450250 (−0.0032582201 to 0.0074799170) | `tables/cindex_bootstrap_contrasts.csv` |
| PhysioRisk − PhenoAge NCP acceleration C | 0.0162522486 (−0.0004944793 to 0.0328506824) | `tables/cindex_bootstrap_contrasts.csv` |
| Five-year predicted / KM observed; fixed-horizon slope; Brier | 0.0461006266 / 0.0465326043; 0.9410220536; 0.0377583313 | `tables/calibration_fixed_horizons.csv` |
| Eight-year predicted / KM observed; fixed-horizon slope; Brier | 0.0857095923 / 0.0882555498; 0.9990292491; 0.0601773827 | `tables/calibration_fixed_horizons.csv` |
| Global Cox calibration slope | 0.8107540546 (0.7621117380–0.8593963712) | `tables/calibration_fixed_horizons.csv` |
| CalibratedTotalRisk PH test | statistic 16.53945455; p=0.00004764823 | `tables/ph_diagnostics.csv` |
| DemoRisk / PhysioRisk PH tests | p=0.08720586 / 0.11627106 | `tables/ph_diagnostics.csv` |
| CalibratedTotalRisk log-time interaction | 0.1712600018 (0.0655465203–0.2769734833), p=0.00149724 | `tables/ph_time_interaction.csv` |
| Follow-up / horizon support | reverse-KM median 74 months; at risk 4,461 at 60 and 1,137 at 96 months | `tables/followup_summary.csv` |
| Uno C and cumulative/dynamic AUC | Exact model-by-horizon values | `tables/censoring_robust_discrimination.csv` |

The submitted PhysioRisk HR 2.7716579077 and submitted TotalRisk HR 1.8774671602 are historical values only. The first arose from a non-converged fit; the second describes the obsolete unit-weight composite. Their provenance is retained in `tables/physiorisk_vs_phenoage_aligned_comparison.csv` and `tables/totalrisk_reconstruction_comparison.csv`, not in revised primary claims.

## Section-by-section audit

| Section/location in v2 | Current claim | Problem | Required replacement | Supporting artifact | Reviewer concern addressed |
|---|---|---|---|---|---|
| Abstract—Methods | TotalRisk is the additive recombination of DemoRisk and standardized PhysioRisk; evaluation is limited to C, HR, KM, and age correlation. | Uses the old unit-weight definition and omits uncertainty, calibration, PH, and censoring-robust validation. | Define training-calibrated recombination; state the split and expanded validation methods. | `totalrisk_training_coefficients.csv`; Sprint 2 CSVs | Composite scale; validation completeness |
| Abstract—Results | TotalRisk “matched” comparator; PhysioRisk had a stronger gradient than acceleration. | Lacks exact estimates and uncertainty; gradient comparison relies on obsolete HR 2.77. | Report corrected PhysioRisk HR, CalibratedTotalRisk C, paired contrasts, and conservative comparator conclusions. | `validation_v2.csv`; `cindex_bootstrap_contrasts.csv` | Convergence; uncertainty; overclaiming |
| Introduction—final paragraphs / Risk decomposition framework | Combined model “recovers overall predictive performance”; additive LP decomposition is implied. | Research question is diffuse; old mathematical equivalence is foreshadowed. | Ask whether demographic and age-adjusted physiological risk can be separated while preserving useful prognostic information; make decomposition—not superiority—the novelty. | Sprint 1 findings; Sprint 2 findings | Study intent and novelty |
| Methods—Study population | General restriction to adults with mortality linkage and sufficient biomarkers. | Omits complete source-to-analysis flow, exact cycle split, upstream missingness, and included/excluded comparison. | Report 92,062 → 53,255/9,104 → 19,829/2,936 → 13,090/2,520 and 6,739/416; describe 1999–2010 development and 2011–2016 validation. | `cohort_flow.csv`; S3D provenance | Cohort flow; temporal separation |
| Methods—Study population / Table 1 | Cycle counts are presented without the reconstructed downstream flow. | Table 1 does not document analytic selection; later-cycle examined counts remain manual/external provenance. | Rebuild Table 1 programmatically from source-cycle and flow artifacts, retaining an explicit provenance footnote. | `s3d_nhanes_input_manifest.csv`; `cohort_flow.csv`; S3D provenance | Table 1 provenance |
| Methods—Study population | NHANES is nationally representative; analysis is unweighted. | Could be read as claiming analytic-cohort population representativeness. | State that NHANES uses a national sampling design but these unweighted complete-case analytic-cohort estimates are not population-representative NHANES estimates. | S3D provenance; current Methods | Survey-weight interpretation |
| Methods—Missing data | PhysioRisk uses cohort-specific complete cases while PhenoAge NCP uses training-median imputation. | Does not describe upstream biomarker missingness, the historical EXTENDED_16 complete-case rule, or common-cohort sensitivity. | Describe cycle-level missingness before complete-case restriction, EXTENDED_16 selection, included/excluded comparison, and the common complete-case/no-op sensitivity. | `missingness_by_cycle.csv`; `cohort_included_excluded_characteristics.csv`; `comparator_sensitivity.csv` | Missingness and fairness |
| Methods—DemoRisk | DemoRisk fitted once in training and frozen. | Substantively correct; terminology must remain DemoRisk in prose while acknowledging legacy code only in provenance. | Retain and sharpen; specify 1999–2010 fit and unchanged prediction in 2011–2016. | S1 canonical reconstruction | Development/validation separation |
| Methods—Axis identification/model selection | PCA and later ablation supported the two-axis choice. | Wording risks implying selection using temporal validation; exact two-axis producer details are incomplete. | State exploratory/training-derived construction and that the frozen two-axis score was evaluated without temporal refitting; avoid unsupported selection detail. | S1 canonical reconstruction; model lock | Test-set leakage/model selection |
| Methods—PhysioRisk construction | Rounded 0.433/0.235 coefficients are presented as exact fitted coefficients; submitted HR workflow is not qualified. | Exact raw coefficients/standardization parameters are unavailable; current HR 2.77 was non-converged. | Label 0.433/0.235 as rounded raw-score coefficients; distinguish raw from training-standardized score; describe convergence-controlled evaluation per actual test SD. | `totalrisk_raw_identity_diagnostics.csv`; `validation_v2.csv` | Reproducibility; HR convergence |
| Methods—TotalRisk construction / theoretical framework | `TotalRisk = DemoRisk + PhysioRisk`; claimed to preserve a joint Cox LP and multiplicative hazard decomposition. | Standardization changed relative coefficient scale, so unit weights are not generally the joint Cox LP. | Describe submitted score as a useful historical ranking score; define `CalibratedTotalRisk = 1.0586578127615558×DemoRisk + 0.3563514638575306×PhysioRisk`; training-only fit and freeze; no temporal selection. | `totalrisk_training_coefficients.csv`; S1 findings | Composite justification and scale |
| Methods—Comparator | Uses “PhenoAge no-CRP proxy,” “Levine-style,” and abbreviations inconsistently. | Terminology is variable and can suggest exact PhenoAge replication. | Use “PhenoAge NCP” or “PhenoAge no-CRP proxy” consistently; explain omitted CRP and constrained proxy status. | S1 canonical reconstruction | Comparator validity |
| Methods—Model evaluation | Four metrics only; no uncertainty, direct contrasts, calibration, PH, or IPCW discrimination. | Incomplete relative to frozen Sprint 2 analysis. | Add convergence control, actual test-SD scaling, 2,000 participant bootstrap CIs, paired contrasts, Schoenfeld tests, diagnostic log-time interaction, 5/8-year calibration, IPCW Brier, Uno C, AUC, and common complete-case sensitivity. | Sprint 2 CSV suite | Statistical validation requests |
| Methods—Model formulation and theoretical framework | Duplicates preceding Methods and repeats old unit-weight equation. | Duplicated Methods material and mathematically obsolete definition. | Consolidate into the score-construction subsections; remove duplicate theoretical section. | S1 findings | Clarity; composite scale |
| Results—cohort paragraph | Only 13,090 training and 6,739 test are described. | Outdated/incomplete cohort flow and no selection comparison. | Add all reconstructed stages, deaths, included/excluded differences, follow-up, and analytic-cohort limitation. | `cohort_flow.csv`; `cohort_included_excluded_characteristics.csv`; `followup_summary.csv` | Cohort flow/generalizability |
| Results—Table 2 | DemoRisk C 0.827/HR 3.74; PhysioRisk C 0.654/HR 2.77; original TotalRisk C 0.840/HR 1.88. | PhysioRisk HR is non-converged; original TotalRisk is no longer primary; no C-index CIs. | Replace with repaired five-row table including bootstrap CIs, corrected HRs, and CalibratedTotalRisk. | `validation_v2.csv` | Convergence; uncertainty; repaired composite |
| Results—overall comparison | PhenoAge NCP “achieved the highest” and TotalRisk was nearly identical. | Uses obsolete TotalRisk and no paired uncertainty. | Report CalibratedTotalRisk vs PhenoAge NCP ΔC=0.00205 (95% CI −0.00326 to 0.00748); no established difference. | `cindex_bootstrap_contrasts.csv` | Fair comparator claim |
| Results—component ablation | Recombination increased discrimination relative to DemoRisk. | Direction is correct but unsupported by uncertainty and old recombination. | Report CalibratedTotalRisk − DemoRisk ΔC=0.01628 (0.01109–0.02199). | `cindex_bootstrap_contrasts.csv` | Incremental value |
| Results—physiology-only comparison | PhysioRisk has a “substantially stronger” HR (~2.8 vs 1.4) and clearer separation. | Central comparison rests on non-converged HR; implies clear superiority without paired-C uncertainty. | Report corrected HR 1.387; describe C-index advantage over acceleration as suggestive because CI narrowly crosses zero. | `validation_v2.csv`; `cindex_bootstrap_contrasts.csv` | HR convergence; superiority overclaim |
| Results—summary / Figure 2 caption | PhysioRisk showed stronger risk separation; figure displays obsolete HR. | Obsolete numerical panel and overclaim. | Regenerate before reuse or remove from revised main text; use uncertainty-aware discrimination framing. | `validation_v2.csv`; figure audit | Figure accuracy |
| Results—missing validation domains | No calibration, PH, Uno C/AUC, or comparator sensitivity results. | Contradicts completed frozen evidence by omission and leaves outdated limitation claims. | Add concise main-text results; move detailed diagnostics to supplement. | Sprint 2 CSV suite | Calibration, PH, censoring, sensitivity |
| Discussion—Principal findings | PhysioRisk “showed stronger mortality risk separation” than acceleration. | Not established by paired percentile CI; HR basis obsolete. | Call the C-index difference suggestive, not conclusive; emphasize residual physiological information. | `cindex_bootstrap_contrasts.csv` | Overclaiming |
| Discussion—Interpretation | TotalRisk recombines components “on the log-hazard scale.” | Without calibrated coefficients this repeats unit-weight error. | Discuss training-calibrated recombination and its incremental discrimination. | `totalrisk_training_coefficients.csv`; contrasts | Composite interpretation |
| Discussion—Limitations | Says analysis emphasized ranking rather than absolute-risk calibration. | Directly inconsistent with completed fixed-horizon calibration. | Replace with actual 5/8-year findings, lack of slope CIs, and eight-year tail qualification. | `calibration_fixed_horizons.csv`; `followup_summary.csv` | Calibration |
| Discussion—Limitations | No PH limitation. | CalibratedTotalRisk violates strict PH. | State violation and strengthening association; do not label global slope simply as overfitting; keep time-interaction diagnostic separate. | `ph_diagnostics.csv`; `ph_time_interaction.csv` | PH assumption |
| Discussion—Limitations | Complete-case selection only briefly noted; population representativeness could remain ambiguous. | Omits 33,426 excluded and observed included/excluded differences. | Discuss selection, upstream missingness, unweighted analytic-cohort scope, and limited generalizability. | S3D CSVs | Cohort selection |
| Discussion/Future directions | External validation is required. | Correct only if consistently framed as outstanding, not as completed. | Retain explicitly as future work; use “internal temporal validation” throughout current evidence. | S2 findings | External validation wording |
| Abstract—written last | Current abstract lacks repaired estimates and limitations. | Cannot remain aligned after Methods/Results repair. | Rewrite last from revised Methods, Results, Table 2, and limitations. | All canonical artifacts | Cross-section consistency |

## Explicit search findings before revision

| Search target | Finding in current manuscript | Classification before edit |
|---|---|---|
| BaselineRisk | Not used in visible manuscript prose; appears in legacy code/provenance elsewhere. | Current/correct in technical provenance only |
| Old TotalRisk definition / unit weight | Methods, theoretical framework, Results, Discussion, Table 2, Figure 2. | Obsolete and requiring replacement |
| PhysioRisk HR about 2.77 | Table 2, physiology-only Results, Figure 2. | Obsolete current claim; historical only |
| TotalRisk HR about 1.88 | Table 2 and Figure 2. | Obsolete primary-model claim; historical only |
| 0.433 / 0.235 | PhysioRisk Methods. | Retain only as rounded raw-score coefficients with provenance qualification |
| Superiority/outperformance vs PhenoAge | No literal “outperform” in extracted prose, but “stronger risk separation” and “clearer” are functionally stronger claims. | Weaken to uncertainty-aware comparison |
| External validation | Reporting framework, Limitations, Future directions. | Correct if consistently outstanding |
| PH findings | Absent from current Results/Discussion. | Requires addition |
| Calibration findings | Current limitation says calibration remains future work. | Obsolete and requiring replacement |
| Cohort flow/missingness | Incomplete and pre-Sprint-3D. | Obsolete and requiring replacement |
| Population representation | NHANES described as nationally representative; unweighted caveat appears later. | Clarify analytic cohort is not population representative |
| Duplicated Methods/Results | “Model formulation and theoretical framework” duplicates construction; Results repeats benchmark interpretation in several subsections. | Consolidate |
| Development vs validation | Training freeze is stated but cycle boundaries and diagnostic refits are unclear. | Clarify 1999–2010 vs 2011–2016 and diagnostic-only temporal fits |

## Planned main text versus supplement

Main text: reconstructed participant flow; compact included/excluded summary; repaired Table 2; paired CalibratedTotalRisk contrasts; concise fixed-horizon calibration and PH findings; concise censoring-robust confirmation.

Supplement: full paired bootstrap contrast table; detailed PH and Schoenfeld summaries; diagnostic time-interaction estimates; horizon-specific calibration metrics and decile data; Uno C/AUC table; cycle-specific missingness; full included/excluded table; common-cohort comparator sensitivity; historical submitted TotalRisk and submitted non-converged PhysioRisk HR, explicitly labeled.

## Figure audit decision

- Existing Figure 1 (quartile Kaplan–Meier comparison): potentially informative but its caption makes an unqualified “clearer separation” claim. Retain only with a descriptive, non-superiority caption or move to supplement.
- Existing Figure 2: must not be reused because its HR panel contains the non-converged PhysioRisk estimate and the obsolete primary TotalRisk.
- Recommended main figure: 5- and 8-year calibration curves generated directly from `tables/calibration_plot_data.csv`; this adds evidence not conveyed by Table 2.
- Recommended optional conceptual figure: a compact diagram showing DemoRisk and age/sex-residualized PhysioRisk entering the training-calibrated composite. Defer cosmetic production because no existing analysis output directly generates it.
- Optional flow diagram: useful if journal space permits; counts must come from `tables/cohort_flow.csv`.
