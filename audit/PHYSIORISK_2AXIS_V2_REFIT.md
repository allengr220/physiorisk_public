# PhysioRisk_2axis_v2 Refit

## Scope and lineage

PhysioRisk_2axis_v2 was refit from the corrected creatinine inputs frozen at
parent commit `40cfbdbe187789207d74bae9f803f319f63cb3de`. Cohort membership,
the temporal split, biomarkers, residualization, axis definitions, endpoint,
Cox model form, and penalizer are unchanged from v1.

The historical `BaselineRisk` column was joined by `SEQN` and verified exactly
unchanged for every participant. In scientific reporting this component is
DemoRisk. DemoRisk was not recomputed or refit.

- Development: 13,090 participants and 2,520 deaths.
- Validation: 6,739 participants and 416 deaths.
- Development and validation ID sets are exactly identical to v1.
- Historical v1 artifacts were not overwritten.
- The separate 1999–2000 creatinine assay correction was not applied.

## Locked residualization and axes

Residualizers use development-only median imputation and linear regression on
`cr(RIDAGEYR, df=4) + RIAGENDR`. Residuals use the development population SD
(`ddof=0`) and the historical `+ 1e-8` denominator. Development transforms are
applied unchanged to validation.

Axis definitions:

- `HematologicStress = mean(LBXWBCSI_resid_z, -LBXLYPCT_resid_z,
  LBXMCV_resid_z, LBXRDW_resid_z)`
- `RenalHepaticTurnover = mean(LBXSCR_resid_z, -LBXSAL_resid_z,
  LBXSAPSI_resid_z)`

All four hematologic constituent residuals were exactly unchanged in both
cohorts. HematologicStress agreed with v1 to floating-point precision (maximum
absolute difference `1.78e-15`). Corrected development creatinine residual SD
before standardization was `0.360077921269864`; its standardized development
mean was `4.34e-18` and SD was `0.9999999722282341`.

## Fitted model

The development-only two-axis Cox model uses penalizer `0.01` and `l1_ratio=0`.
The coefficients, standardization parameters, and validation statistics below
are computed model outputs. The independent target values are consulted only
after fitting as reconciliation checks and are not used to construct scores or
set fitted parameters.

| Axis | Native-axis coefficient | Final standardized-score weight |
|---|---:|---:|
| HematologicStress | 0.41878905476678663 | 1.4992102570115298 |
| RenalHepaticTurnover | 0.23946732365058307 | 0.8572618213147398 |

The raw development log-partial-hazard mean was
`-5.970947359328573e-18`; its sample SD was `0.2793397742632746`.
PhysioRisk_2axis_v2 is `(raw score - development mean) / development sample SD`.

## Temporal validation

| Score | HR per validation SD | 95% CI | p | Harrell C | Corr(age) |
|---|---:|---:|---:|---:|---:|
| HematologicStress | 1.3053066492687337 | 1.2608638190397687–1.351315996935137 | 2.3685207434534356e-51 | 0.63603813285264 | 0.08286705313898898 |
| RenalHepaticTurnover | 1.1921158116375161 | 1.158093175581169–1.227137969829586 | 1.2536265830587564e-32 | 0.6175565976367979 | 0.07427979831155705 |
| PhysioRisk_2axis_v2 | 1.3849333672986084 | 1.3354291617335998–1.4362726880751502 | 7.729271990365634e-69 | 0.663181826218942 | 0.10165744783787456 |

## Old-versus-corrected reconciliation

| Quantity | Development | Validation |
|---|---:|---:|
| RHT Pearson | 0.7713589953728056 | 0.8039014709190222 |
| RHT Spearman | 0.7899174279817515 | 0.9155523569962603 |
| RHT mean absolute difference | 0.24757313576100085 | 0.1808387825385963 |
| RHT SD of paired difference | 0.4064851460154277 | 0.3596642034606166 |
| RHT changed decile | 68.38808250572956% | 57.33788395904437% |
| PhysioRisk Pearson | 0.9405587593876755 | 0.9527846602166798 |
| PhysioRisk Spearman | 0.9442768372348033 | 0.9826341165962028 |
| PhysioRisk mean absolute difference | 0.21022283331058253 | 0.15109458682907978 |
| PhysioRisk SD of paired difference | 0.3447933891835063 | 0.30805671592165773 |

The affected 2001–2002 development-cycle mean RenalHepaticTurnover changed from
`0.651849779101439` to `0.032824033243237336`. All independent audit targets
reconciled.

## Artifacts

The executable producer is `scripts/refit_physiorisk_2axis_v2.py`. Versioned
inputs, residual/axis artifacts, scored parquets, coefficient and validation
tables, full residualizer/model metadata, reconciliation results, and the hash
manifest are under `outputs/physiorisk_2axis_v2_refit/`. The machine-readable
repository provenance record is `audit/physiorisk_2axis_v2_provenance.json`.

The six participant-level parquet files are ignored by Git and remain local or
external. They are not part of this checkpoint commit. Their canonical paths,
row counts, schema summaries, and hashes are:

| Artifact | Rows | Schema summary | SHA256 |
|---|---:|---|---|
| `/home/ubuntu2204/longevity/physiorisk_public/outputs/physiorisk_2axis_v2_refit/physiorisk_2axis_v2_train_input_levinenocrp.parquet` | 13,090 | `SEQN:int64`; 13 `double` analysis fields; `cycle_start_year:int64` | `c7b6cdea0f7d80ce104e950fefd16438c895801fb8bd8c37be63fe9849ee9c5a` |
| `/home/ubuntu2204/longevity/physiorisk_public/outputs/physiorisk_2axis_v2_refit/physiorisk_2axis_v2_test_input_levinenocrp.parquet` | 6,739 | `SEQN:int64`; 13 `double` analysis fields; `cycle_start_year:int64` | `1518aa23840eb0cd6678e7f925d4c0d9c44199b7e67fee536f6cea02308923d4` |
| `/home/ubuntu2204/longevity/physiorisk_public/outputs/physiorisk_2axis_v2_refit/physiorisk_2axis_v2_train_axes_levinenocrp.parquet` | 13,090 | `SEQN:int64`; 7 residual `double` fields; 2 axis `double` fields | `772e0b75498b0fc4c9a4b73071c35dc5dca2fff2da833eacad560eaf2cb48897` |
| `/home/ubuntu2204/longevity/physiorisk_public/outputs/physiorisk_2axis_v2_refit/physiorisk_2axis_v2_test_axes_levinenocrp.parquet` | 6,739 | `SEQN:int64`; 7 residual `double` fields; 2 axis `double` fields | `bde2937c1f787140c15b9c22116ddb561965b86277382abd5136c542d56b0cbe` |
| `/home/ubuntu2204/longevity/physiorisk_public/outputs/physiorisk_2axis_v2_refit/physiorisk_2axis_v2_train_scored_levinenocrp.parquet` | 13,090 | input schema plus 2 axis `double` fields and `PhysioRisk_2axis_v2:double` | `578b08930f8ea524e205a6d7754b2c07739ed775d081346b39e24fd27890cab1` |
| `/home/ubuntu2204/longevity/physiorisk_public/outputs/physiorisk_2axis_v2_refit/physiorisk_2axis_v2_test_scored_levinenocrp.parquet` | 6,739 | input schema plus 2 axis `double` fields and `PhysioRisk_2axis_v2:double` | `e623e1e0d59da80e616a29a32821ab35552601864b650f239fde2566c362920d` |

The lightweight coefficient table, validation table, reconciliation summary,
model metadata, and artifact hash manifest are included in the repository
checkpoint.

## Deferred work

CalibratedTotalRisk was not refit or evaluated. No TotalRisk field is present in
the v2 scored artifacts.

Notebook 05 constructs PhenoAge NCP directly from creatinine through the term
`0.0095 * LBXSCR`. The next phase must recompute development and validation
PhenoAge NCP values, refit the development-only NCP age/sex acceleration model,
apply that frozen acceleration model to validation, and recompute comparator
metrics. No PhenoAge NCP or comparator output was modified in this phase.

The separate 1999–2000 creatinine assay-standardization correction remains out
of scope. Historical submitted artifacts and journal packages remain unchanged.
