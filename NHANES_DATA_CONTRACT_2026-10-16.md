# NHANES data contract — 2026-10-16

This is a reusable ingestion and provenance contract. It describes data handling used by the current pipeline; it does not specify a PhysioRisk or RSE model.

## Dataset scope

The contract covers the nine NHANES continuous cycles: 1999–2000, 2001–2002, 2003–2004, 2005–2006, 2007–2008, 2009–2010, 2011–2012, 2013–2014, and 2015–2016. Each record carries `cycle_start_year` and the source cycle label.

`SEQN` is the participant identifier. The mortality input is the NCHS public 2019 Linked Mortality File release. Its required fields are `ELIGSTAT` (mortality eligibility), `PERMTH_INT` (person-months of follow-up), and `MORTSTAT` (death status). The fixed-width mortality parser also retains `PERMTH_EXM` where supplied.

## Join contract

- Normalize `SEQN` to a numeric nullable integer before every merge.
- Require `SEQN` to be unique within each source-cycle assembled participant frame and within each mortality-cycle input.
- Join the source-cycle frame to mortality on `SEQN` with a left, one-to-one merge.
- Fail on duplicate identifiers, merge-cardinality failure, missing required mortality fields among records represented as eligible, or a mortality-input cycle count that differs from the matching source-cycle count.
- Retain cycle identity on both sides of the linkage and fail if a linked mortality record belongs to a different cycle.
- Record unmatched source identifiers and do not silently coerce them into eligibility. Expected survival eligibility is determined only after the linkage and the documented eligibility filter.

The staged regeneration inventory is `tables/s3d_nhanes_input_manifest.csv`; its output and checksum record is `tables/s3d_regeneration_manifest.json`.

## Cohort construction

The following rules are executable cohort rules, in order:

1. Read and assemble the nine source-cycle participant frames; concatenate them after requiring unique `SEQN`. Expected source N is 92,062.
2. Parse and concatenate the matching public mortality files; deduplicate only after requiring that a duplicate cannot silently alter a participant linkage.
3. Left-join mortality to participants using the join contract.
4. Define the mortality-eligible denominator as `ELIGSTAT == 1`, `PERMTH_INT` nonmissing, and `MORTSTAT` nonmissing. Expected N/deaths: 53,255/9,104.
5. Define `EXTENDED_16` completeness as nonmissing values for `BMXBMI`, `BMXWAIST`, `BPXSY1`, `BPXDI1`, `LBXGH`, `LBDHDD`, `LBXTC`, `LBXTR`, `LBXSAL`, `LBXSCR`, `LBXSAPSI`, `LBXWBCSI`, `LBXLYPCT`, `LBXGLU`, `LBXMCV`, and `LBXRDW`. Expected N/deaths: 19,829/2,936.
6. The eight-biomarker comparison set requires nonmissing `LBXSAL`, `LBXSCR`, `LBXGLU`, `LBXLYPCT`, `LBXMCV`, `LBXRDW`, `LBXSAPSI`, and `LBXWBCSI`. Within the `EXTENDED_16` cohort it adds no participants and removes none.
7. Assign development to `cycle_start_year <= 2010` and temporal validation to `cycle_start_year >= 2011`. Expected development N/deaths: 13,090/2,520. Expected temporal N/deaths: 6,739/416.

These totals are computed values with expected-value assertions in `scripts/run_s3d_cohort_regeneration.py`. Do not use an expected total to create, fill, or select records.

## Source-variable contract

All source selections must retain source file, source variable, native unit, conversion, cycle, and harmonized-unit metadata. Variable aliases in the cycle loader are compatibility candidates, not permission for silent substitution: a newly selected alias requires an explicit source-unit check and an updated manifest.

| Conceptual variable | Current source variable(s) | Cycles | Native to harmonized unit / conversion | Missingness and cycle exception |
|---|---|---|---|---|
| Identifier and demographics | `SEQN`, `RIDAGEYR`, `RIAGENDR`, `RIDRETH3` (`RIDRETH1` fallback) from DEMO | All nine | Identifier, years, categorical fields; no conversion | Required identifier; record demographic-source fallback in metadata |
| Body mass index | `BMXBMI` | All | kg/m²; direct | Included in `EXTENDED_16` |
| Waist | `BMXWAIST` | All | cm; direct | Included in `EXTENDED_16` |
| Systolic blood pressure | `BPXSY1` | All | mmHg; direct | Included in `EXTENDED_16` |
| Diastolic blood pressure | `BPXDI1` | All | mmHg; direct | Included in `EXTENDED_16` |
| Glycohemoglobin | `LBXGH` (`LB2GH` fallback) | All | percent; direct after codebook verification | Included in `EXTENDED_16` |
| HDL cholesterol | `LBDHDD`, `LBXHDD`, `LBDHDL`, or `LBXHDDSI` | All as available | Record native codebook unit and explicit mapping to the pipeline analytic unit | Included in `EXTENDED_16`; no silent SI/conventional substitution |
| Total cholesterol | `LBXTC`, `LB2TCH`, or `LB2SCH` | All as available | Record native codebook unit and explicit mapping to the pipeline analytic unit | Included in `EXTENDED_16` |
| Triglycerides | `LBXTR`, `LB2TR`, or `LBDTRSI` | All as available | Record native codebook unit and explicit mapping to the pipeline analytic unit | Included in `EXTENDED_16`; no silent SI/conventional substitution |
| Albumin | `LBXSAL`, `LBDSALSI`, `LB2SAL`, or `LB2AL` | All as available | Pipeline canonical input is g/dL. PhenoAge NCP uses g/L = g/dL × 10 | Included in `EXTENDED_16` |
| Creatinine | 1999–2000 `LAB18.XPT:LBXSCR`; 2001–2002 `L40_B.XPT:LBDSCR` (SI fallback `LBDSCRSI` only); 2003–2004 `L40_C.XPT:LBXSCR`; 2005–2016 `BIOPRO_[D:I].XPT:LBXSCR` | All | Canonical pipeline value `LBXSCR` is mg/dL. If the 2001–2002 SI fallback is necessary, divide µmol/L by 88.4. PhenoAge NCP uses µmol/L = mg/dL × 88.4; PhysioRisk uses mg/dL | Included in `EXTENDED_16`. Reconcile simultaneous 2001–2002 conventional/SI values within the specified tolerance; fail otherwise |
| Alkaline phosphatase | `LBXSAPSI`, `LBDSAPSI`, `LB2SAPSI`, or `LB2AP` | All as available | U/L; direct after codebook verification | Included in `EXTENDED_16` |
| White blood cell count | `LBXWBCSI`, `LBDWBCSI`, or `LBXWBC` | All as available | 10³/µL; direct after codebook verification | Included in `EXTENDED_16` |
| Lymphocyte percentage | `LBXLYPCT`, `LBDLYMNO`, or `LBXLYP` | All as available | percent; direct after codebook verification | Included in `EXTENDED_16` |
| Glucose | 1999–2000 `LAB10AM.XPT:LBXGLU`; 2001–2002 `L40_B.XPT:LBDSGLSI`; 2003–2004 `L40_C.XPT:LBDSGLSI`; 2005–2016 `GLU_[D:I].XPT:LBXGLU` | All | 2001–2002 and 2003–2004: mmol/L directly. 1999–2000 and 2005–2016: mg/dL × 0.05551 = mmol/L | Included in `EXTENDED_16`. Preserve canonical glucose metadata; PhenoAge NCP uses mmol/L linearly |
| Mean corpuscular volume | `LBXMCV`, `LBDMCVSI`, or `LBXMCVSI` | All as available | fL; direct after codebook verification | Included in `EXTENDED_16` |
| Red-cell distribution width | `LBXRDW` or `LBXRDWSI` | All as available | percent; direct after codebook verification | Included in `EXTENDED_16` |

The source inventory also includes body-measurement, blood-pressure, laboratory, glucose, and CBC file family identifiers selected by the notebook cycle loader. Source aliases cannot be chosen based only on column presence; the cycle manifest must identify the actual file and variable used.

For the PhenoAge NCP-specific predictor line, albumin must be g/L, creatinine µmol/L, glucose mmol/L, lymphocyte percentage percent, mean corpuscular volume fL, red-cell distribution width percent, alkaline phosphatase U/L, white blood cell count 10³/µL, and age years. C-reactive protein is not part of that comparator. Glucose enters linearly.

For PhysioRisk-specific reuse, creatinine remains mg/dL. A project may not use the PhenoAge creatinine conversion as a replacement for the PhysioRisk input.

## Missingness and completeness

The mortality-eligible denominator is the 53,255 linked participants satisfying the eligibility and follow-up rule. `EXTENDED_16` completeness is an all-fields complete-case rule over the 16 named variables. The eight-biomarker comparison completeness requirement is a subset of `EXTENDED_16`; it does not further restrict the current benchmark cohort.

Cycle-specific missingness must be reported before complete-case filtering. Missing values remain missing: no implicit imputation, fallback variable substitution, or cross-cycle unit inference is permitted. The principal known cycle exceptions are the 2001–2002 creatinine source contract and the two glucose SI cycles (2001–2002 and 2003–2004).

## Required assertions for future reuse

- Assert source-cycle record counts and their total against the expected public-source values.
- Assert unique `SEQN` within every required input and after assembly.
- Assert one-to-one mortality linkage and report unmatched identifiers.
- Assert plausible post-harmonization domains and ranges, including explicit creatinine and glucose unit checks.
- Assert every conversion is selected by cycle; never infer a conversion silently from a column name or magnitude.
- Assert the 19,829 biomarker-complete cohort and its 2,936 deaths are reproduced when the same public release and rules are used.
- Assert the 13,090/2,520 development and 6,739/416 temporal split is reproduced.
- Assert that no cycle later than 2015–2016 is included.
- Fail if a required source column is absent or an unapproved alias would be substituted.
- Require source-unit metadata on every derived variable and preserve it through each derived table.

## Provenance map

| Derived output | Immediate upstream sources |
|---|---|
| `nhanes_biomarker_master_verified.parquet` | Nine assembled source-cycle frames and `s3d_nhanes_input_manifest.csv` |
| `nhanes_1999_2016_survival_master.parquet` | Participant master plus parsed NCHS linked mortality records |
| `nhanes_1999_2016_extended_mortality_model_dataset.parquet` | Survival master plus the `EXTENDED_16` completeness rule |
| `benchmark_levine_no_crp_cohort.parquet` | Extended model dataset plus the eight-biomarker comparison selection |
| `development_cohort.parquet` / `validation_cohort.parquet` | Benchmark cohort plus `cycle_start_year` split |
| `cohort_flow.csv` / `missingness_by_cycle.csv` | Survival master and completeness indicators |
| `s3d_regeneration_manifest.json` | Input/output manifests and checksum records |

The reusable code paths are notebook 01 (`notebooks/01_nhanes_extended_dataset_builder.ipynb`) and the independently staged verifier `scripts/run_s3d_cohort_regeneration.py`. Raw public source files are external to the repository; `DATA_SOURCES.md`, the input manifest, and the artifact manifest provide their retrieval and provenance record.
