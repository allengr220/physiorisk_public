# Sprint 4 forensic consistency audit

## Scope

Audit target: `manuscript/archive/PhysioRisk_BMC_MIDM_v3_revised.md`, its generated DOCX, and `manuscript/generated/` supplementary outputs. Canonical comparators were the frozen Sprint 1/Sprint 2 CSVs and Sprint 3D provenance. The submitted v2 manuscript remains historical and was not altered.

## Required-term classification

| Search term | Revised-manuscript or supplement occurrence | Classification | Disposition |
|---|---|---|---|
| `2.771`, `2.77` | Methods mentions submitted HR 2.772; Supplementary Table S9 contains exact 2.7716579. | Historical and explicitly labeled | Retained for correction transparency; not used as current inference. |
| `1.877`, `1.88` | Supplementary Table S9 contains exact 1.8774672. | Historical and explicitly labeled | Retained only for obsolete unit-weight TotalRisk provenance. |
| `0.433`, `0.235` | Methods and Limitations. | Current/correct with qualification | Explicitly labeled rounded raw-score coefficients that do not exactly reconstruct the stored score. |
| `BaselineRisk` | DemoRisk Methods legacy-code note; Supplementary Table S9 historical score identifier. | Historical/technical and explicitly labeled | No current prose uses it as the manuscript score name. |
| `DemoRisk` | Throughout primary manuscript and tables. | Current/correct | Canonical prose term. |
| `TotalRisk` | Primary claims use `CalibratedTotalRisk`; unqualified/submitted TotalRisk appears only in historical correction text and S9. | Current/correct or historical and explicitly labeled | No obsolete unit-weight score is presented as primary. |
| `unit-weight` | Methods, Discussion, figure plan, and historical table label. | Historical and explicitly labeled | Used to explain the repaired scale mismatch. |
| `external validation` | Abstract, Limitations, Conclusions, reviewer map. | Current/correct | Always described as necessary/outstanding, never completed. |
| `outperform` | No occurrence in revised primary manuscript. | Current/correct | Removed. |
| `superior` / `superiority` | Only negated statements and non-superiority figure guidance. | Current/correct | No superiority claim remains. |
| `PhenoAge` | Throughout comparator Methods/Results/Discussion. | Current/correct | Consistently `PhenoAge NCP` or `PhenoAge no-CRP proxy`; full PhenoAge equivalence is denied. |
| `proportional hazards` | Abstract, Methods, Results, Discussion. | Current/correct | CalibratedTotalRisk violation and strengthening association are stated; reference models are not materially flagged. |
| `calibration` | Abstract, Methods, Results, Discussion, generated table and figure plan. | Current/correct | Fixed-horizon and global Cox summaries remain distinct. |
| `biological age` | Introduction and Discussion. | Current/correct | PhysioRisk is explicitly not proof of biological age. |

No obsolete occurrence remains unlabeled in the revised manuscript-facing package.

## Cross-artifact verification

| Check | Result |
|---|---|
| Methods ↔ notebooks/provenance | Pass: cycles, split, training freeze, residualization, score construction, legacy identifier, and diagnostic-only temporal fits agree with canonical documentation. |
| Results ↔ CSVs | Pass: cohort, discrimination, HR, contrasts, calibration, PH, follow-up, Uno C/AUC, and sensitivity values agree after stated rounding. |
| Abstract ↔ Results | Pass: every abstract number appears in Results with the same direction and interpretation. |
| Tables ↔ Results | Pass: programmatic Table 1 uses input manifest/cohort flow; Table 2 uses `validation_v2.csv`. |
| Discussion ↔ evidence | Pass: incremental value is supported; PhenoAge NCP difference is not established; acceleration result is suggestive; calibration and PH interpretations are separated. |
| Terminology | Pass: DemoRisk in prose; CalibratedTotalRisk primary; PhenoAge NCP identified as proxy. |
| Cohort counts ↔ Sprint 3D | Pass: `19,829 + 33,426 = 53,255`; `13,090 + 6,739 = 19,829`; `2,520 + 416 = 2,936`. |
| Development ↔ validation separation | Pass with provenance qualification: the frozen scoring/evaluation path and CalibratedTotalRisk coefficients are training-only; temporal diagnostic fits are explicitly non-predictive. The unavailable original two-axis producer prevents reconstruction of every earlier selection decision. |

## `/review` record

Question: “Does any statement, number, table, figure, or interpretation in the revised manuscript contradict the frozen Sprint 1/Sprint 2 analysis, Sprint 3D cohort provenance, or another section of the manuscript?”

Initial result: no scientific numerical or interpretive contradiction was found. One P2 packaging inconsistency was identified: the review-copy DOCX referred to figures as included/moved although the calibration SVG was standalone and the proposed supplementary Kaplan–Meier figure had not been packaged.

Resolution: manuscript language now calls the calibration SVG a standalone author-placement asset and describes the Kaplan–Meier item as a recommendation, not a completed move. The comparative submitted Figure 2 remains retired.

Second review result: numerical results and cohort counts again passed, but `/review` flagged an overbroad statement that temporal performance never informed original two-axis score selection. The frozen path proves no temporal refitting, whereas the missing original producer cannot reconstruct every prior selection decision. The manuscript now states that limitation and narrows the no-temporal-selection claim to the fully documented CalibratedTotalRisk coefficients.
