# PhysioRisk

PhysioRisk is an interpretable survival-modeling framework for separating demographic and physiological components of all-cause mortality risk using NHANES mortality-linked cohort data.

The project decomposes mortality risk into:

- **DemoRisk**: an age- and sex-based demographic mortality-risk component
- **PhysioRisk**: an age- and sex-residualized physiological-risk component
- **TotalRisk**: recombination of DemoRisk and PhysioRisk on the Cox log-hazard scale

The goal is not to replace existing biological-age or mortality-risk models, but to make their structure more interpretable by distinguishing age-entangled baseline risk from residual physiological variation.

## Current status

The PhysioRisk manuscript has been submitted to *BMC Medical Informatics and Decision Making*, has passed technical checks, and is publicly available as a Research Square preprint.

Research Square DOI: https://doi.org/10.21203/rs.3.rs-9829732/v1

Following external review by *BMC Medical Informatics and Decision Making*, this repository is being consolidated as the canonical public reproducibility artifact. Scientific revisions are not part of the current repository sprint.

## Repository structure

```text
notebooks/
  01_nhanes_extended_dataset_builder.ipynb
  02_benchmark_dataset_builder.ipynb
  03_demographic_risk_model.ipynb
  04_physiorisk_scoring.ipynb
  05_physiorisk_model_validation.ipynb
  06_physiorisk_figures.ipynb
  07_ablation_analysis_optional.ipynb

  # Supplemental post-review notebooks
  07_totalrisk_reconstruction.ipynb
  08_validation_v2.ipynb
  09_cohort_comparator_sensitivity.ipynb

tables/
  README.md

data/
  README.md
  ARTIFACT_MANIFEST.tsv

docs/
  NOTEBOOK_ORDER.md
  ARTIFACT_PROVENANCE.md
  EXPECTED_ARTIFACTS.md
  PIPELINE_AUDIT.md
  PIPELINE_GRAPH.md
  REVIEWER_RESPONSE_MATRIX.md
  SOURCE_NOTEBOOK_PROVENANCE_AUDIT.md
  SPRINT3_GAP_ANALYSIS.md
  SPRINT3_SUMMARY.md
  SPRINT3C_SUMMARY.md

MODEL_LOCK.md
DATA_SOURCES.md
STATUS.md
CITATION.cff
LICENSE
eof
- `notebooks/` — six direct manuscript-pipeline notebooks, one optional historical ablation notebook, and three supplemental post-review notebooks
- `data/` — documentation and manifest only; large participant-level artifacts remain external
- `tables/` — committed validation, calibration, diagnostic, cohort, and sensitivity outputs
- `docs/` — notebook order, artifact provenance, pipeline audit, and reviewer-readiness assessment
- `MODEL_LOCK.md` — frozen model specification
- `DATA_SOURCES.md` — data-source notes
- `STATUS.md` — manuscript and repository status
- `CITATION.cff` — citation metadata

## Notebook order

See `docs/NOTEBOOK_ORDER.md`.

## Data

This project uses publicly available NHANES data and NHANES-linked mortality follow-up files. Raw NHANES data are not included in this repository. See `DATA_SOURCES.md` and `data/ARTIFACT_MANIFEST.tsv`.

Canonical documentation uses manuscript terms **DemoRisk**, **PhysioRisk**, **TotalRisk**, **PhenoAge NCP**, and **PhenoAge NCP acceleration**. Frozen notebook/data identifiers retain historical names such as `BaselineRisk`, `PhysioRisk_2axis`, `TotalRisk_2axis`, `PhenoAge_noCRP_proxy`, and `PhenoAgeAccel`; these identifiers are documented rather than renamed.

## Model lock

The core modeling specification is frozen for the submitted manuscript. See `MODEL_LOCK.md`.

## Related project: Reprogramming Safety Engine

PhysioRisk is the first public module of a broader research direction: the Reprogramming Safety Engine, an open-source interpretation layer for AI-enabled rejuvenation research.

## Contact

Gregory S. Allen, Ph.D.  
Independent biomedical scientist  
Cuenca, Ecuador
EOF
