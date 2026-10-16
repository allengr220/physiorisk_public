# PhenoAge NCP v2 Repair

## Scope and lineage

PhenoAge NCP v2 was constructed from the corrected PhysioRisk v2 cohorts at
parent commit `7abcbc11a3eda981b2f4d88e385cb0486f1ed6d7`. Development contains
13,090 participants and 2,520 deaths; validation contains 6,739 participants
and 416 deaths. Both participant-ID sets are exactly identical to the frozen
historical v1 and PhysioRisk v2 cohorts.

The historical implementation was reproduced exactly before correction. It
used native `LBXSAL`, `LBXSCR`, and mixed-unit `LBXGLU` aliases directly,
applied `ln(LBXGLU)`, and used `0.0019` for alkaline phosphatase. Its validation
raw and acceleration metrics reproduce the frozen comparison table.

## Published-form no-CRP contract

The corrected linear predictor is:

```text
PhenoAge_NCP_v2 =
  -19.907
  - 0.0336  * albumin_g_L
  + 0.0095  * creatinine_umol_L
  + 0.1953  * glucose_mmol_L
  - 0.0120  * lymphocyte_pct
  + 0.0268  * MCV_fL
  + 0.3306  * RDW_pct
  + 0.00188 * alkaline_phosphatase_U_L
  + 0.0554  * WBC_10e3_uL
  + 0.0804  * age_years
```

CRP is omitted by design. Glucose is linear and is not log transformed.

| Input | Canonical column/unit | Coefficient unit | Conversion |
|---|---|---|---|
| Albumin | `LBXSAL`, g/dL | g/L | `LBXSAL * 10` |
| Creatinine | `LBXSCR`, mg/dL | µmol/L | `LBXSCR * 88.4` |
| Glucose | `LBXGLU`, cycle-specific | mmol/L | Explicit cycle/source contract below |
| Lymphocytes | `LBXLYPCT`, % | % | None |
| MCV | `LBXMCV`, fL | fL | None |
| RDW | `LBXRDW`, % | % | None |
| Alkaline phosphatase | `LBXSAPSI`, U/L | U/L | None; coefficient `0.00188` |
| WBC | `LBXWBCSI`, 10^3/µL | 10^3/µL | None |
| Age | `RIDAGEYR`, years | years | None |

### Glucose cycle/source contract

| Cycle | Source file | Selected source | Source unit | Target unit | Conversion |
|---|---|---|---|---|---|
| 1999–2000 | `LAB10AM.XPT` | `LBXGLU` | mg/dL | mmol/L | `LBXGLU * 0.05551` |
| 2001–2002 | `L40_B.XPT` | `LBDSGLSI` | mmol/L | mmol/L | Direct |
| 2003–2004 | `L40_C.XPT` | `LBDSGLSI` | mmol/L | mmol/L | Direct |
| 2005–2006 | `GLU_D.XPT` | `LBXGLU` | mg/dL | mmol/L | `LBXGLU * 0.05551` |
| 2007–2008 | `GLU_E.XPT` | `LBXGLU` | mg/dL | mmol/L | `LBXGLU * 0.05551` |
| 2009–2010 | `GLU_F.XPT` | `LBXGLU` | mg/dL | mmol/L | `LBXGLU * 0.05551` |
| 2011–2012 | `GLU_G.XPT` | `LBXGLU` | mg/dL | mmol/L | `LBXGLU * 0.05551` |
| 2013–2014 | `GLU_H.XPT` | `LBXGLU` | mg/dL | mmol/L | `LBXGLU * 0.05551` |
| 2015–2016 | `GLU_I.XPT` | `LBXGLU` | mg/dL | mmol/L | `LBXGLU * 0.05551` |

## Imputation and acceleration

The historical development-median imputation convention was retained. No
development or validation participant had a missing comparator biomarker, so
no value required imputation.

The development-only acceleration model is exactly:

```text
PhenoAge_NCP_v2 ~ cr(RIDAGEYR, df=4) + C(RIAGENDR)
```

The development design and fitted linear regression were applied unchanged to
validation. Exact knots, coefficients, intercept, medians, and design columns
are recorded in
`outputs/phenoage_ncp_v2/phenoage_ncp_v2_acceleration_model_metadata.json`.

## Validation

| Score | HR per validation SD | 95% CI | p | Harrell C | Corr(age) |
|---|---:|---:|---:|---:|---:|
| `PhenoAge_NCP_v2` | 2.3095887816385274 | 2.2047150442291525–2.41945114595776 | 5.075254666024988e-273 | 0.8447479384566133 | 0.9231196422719159 |
| `PhenoAge_NCP_acceleration_v2` | 1.2980038708129953 | 1.256471395923165–1.3409091954756667 | 1.106570894254649e-55 | 0.654344247267949 | 0.05088606117164435 |

## Historical-versus-corrected reconciliation

| Score/cohort | Pearson | Spearman | Mean absolute difference |
|---|---:|---:|---:|
| Raw, development | 0.9674331419680366 | 0.9782956890856499 | 0.46856882482512036 |
| Raw, validation | 0.9674282285942107 | 0.9815103297285837 | 0.4612688790630409 |
| Acceleration, development | 0.700916394284934 | 0.6919600715705471 | 0.31124732124754 |
| Acceleration, validation | 0.7655312785243786 | 0.8634747561073406 | 0.2577461582250486 |

All independent historical, corrected, and reconciliation targets passed.

## Paired PhysioRisk comparison

The participant-level paired bootstrap used 2,000 replicates and seed
`20260821`, matching the manuscript convention.

- PhysioRisk_2axis_v2 C-index: `0.663181826218942`
- PhenoAge_NCP_acceleration_v2 C-index: `0.654344247267949`
- Delta C, PhysioRisk minus acceleration: `0.008837578950992908`
- Percentile 95% CI: `-0.011603816432397801` to `0.028924588788065912`
- Completed replicates: `2000`
- Bootstrap failures: `0`
- Eventless redraws: `0`

## Artifacts and safety

The executable producer is `scripts/build_phenoage_ncp_v2.py`. Outputs and the
hash manifest are under `outputs/phenoage_ncp_v2/`. Machine-readable provenance
is in `audit/phenoage_ncp_v2_provenance.json`.

Participant-level artifacts remain ignored/local:

| Artifact | Rows | SHA256 |
|---|---:|---|
| `outputs/phenoage_ncp_v2/phenoage_ncp_v2_development_comparator.parquet` | 13,090 | `c5575a31b94717813316af1d73f27115ef817decd5504cae910cbae3750fbfa8` |
| `outputs/phenoage_ncp_v2/phenoage_ncp_v2_validation_comparator.parquet` | 6,739 | `e3dcbde86a340a3a0d3e007b62d095521f820132137ee6ca201ef882162c4005` |

CalibratedTotalRisk has not been refit. PhysioRisk_2axis_v2 was not altered.
The separate 1999–2000 creatinine assay-standardization correction was not
applied. Historical comparator outputs, submitted artifacts, manuscripts,
supplements, and journal packages remain unchanged.
