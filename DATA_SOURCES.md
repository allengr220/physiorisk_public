# Data sources

PhysioRisk uses publicly available NHANES data and NHANES-linked mortality follow-up data.

## Primary data source

- National Health and Nutrition Examination Survey (NHANES)
- Survey years: 1999–2016
- Data types: demographics, laboratory biomarkers, examination variables, and linked mortality follow-up

## Mortality follow-up

- NHANES-linked mortality follow-up files
- Outcome: all-cause mortality
- Time variable used in modeling: `PERMTH_INT`
- Event variable used in modeling: `MORTSTAT`

## Raw data availability

Raw NHANES files are not included in this repository.

Users should obtain NHANES public-use data and linked mortality files directly from CDC/NCHS sources and run the canonical notebooks in the documented order.

Expected derived artifacts, producer notebooks, consumers, and Google Drive/MyDrive storage locations are inventoried in `data/ARTIFACT_MANIFEST.tsv`. Large participant-level artifacts are intentionally excluded from Git.

## Reproducibility note

The canonical notebooks document the analytic workflow used for the submitted manuscript, including cohort construction, demographic-risk modeling, physiological-risk modeling, benchmark comparison, and figure/table generation.

Some exported table files are pending cleanup and will be added in a later release pass.
