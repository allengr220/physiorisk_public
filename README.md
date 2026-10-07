# PhysioRisk

PhysioRisk is an interpretable survival-modeling framework for separating demographic and physiological components of all-cause mortality risk using NHANES mortality-linked cohort data.

The project decomposes mortality risk into:

- **DemoRisk**: an age- and sex-based demographic mortality-risk component
- **PhysioRisk**: an age- and sex-residualized physiological-risk component
- **CalibratedTotalRisk**: recombination of DemoRisk and PhysioRisk on the Cox log-hazard scale

The goal is not to replace existing biological-age or mortality-risk models, but to make their structure more interpretable by distinguishing age-entangled baseline risk from residual physiological variation.

## Current status

The manuscript was rejected after external peer review by *BMC Medical Informatics and Decision Making*. The substantially revised manuscript is publicly posted as Research Square Version 2 (6 October 2026): https://www.researchsquare.com/article/rs-9829732/v2

Research Square v2 DOI: https://doi.org/10.21203/rs.3.rs-9829732/v2. Research Square v1 remains a historical preprint record: https://doi.org/10.21203/rs.3.rs-9829732/v1.

This repository is the canonical public reproducibility artifact for the substantially revised v2 analysis and manuscript package. Its validation is internal temporal validation; external independent validation remains outstanding.

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
```

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

## Data and reproducibility

Raw NHANES and public-use mortality files are obtained from CDC/NCHS. Participant-level analytic datasets and score files are not redistributed; the notebooks and scripts reproduce those artifacts from the public inputs, subject to the documented external-artifact and environment requirements. Aggregate manuscript and result tables are committed. Supplementary Tables S1–S9 are in `manuscript/PhysioRisk_RS_Supplementary_Material.*`. Provenance and hashes are documented in `data/ARTIFACT_MANIFEST.tsv` and `docs/ARTIFACT_PROVENANCE.md`.

Canonical documentation uses the revised manuscript terms **DemoRisk**, **PhysioRisk**, **CalibratedTotalRisk**, **PhenoAge NCP**, and **PhenoAge NCP acceleration**. Frozen notebook/data identifiers retain historical names such as `BaselineRisk`, `PhysioRisk_2axis`, `TotalRisk_2axis`, `PhenoAge_noCRP_proxy`, and `PhenoAgeAccel`; these identifiers are documented rather than renamed. Frozen historical notebook source also retains environment-specific Google Drive/MyDrive paths; these are workflow history and portability limitations, not bundled data or credentials.

## Model lock

The core modeling specification remains frozen. See `MODEL_LOCK.md`.

## Related project: Reprogramming Safety Engine

PhysioRisk is intended as the first public module of a broader research direction: the Reprogramming Safety Engine, an open-source interpretation layer for AI-enabled rejuvenation research.

## Contact

Gregory S. Allen, Ph.D.  
Independent biomedical scientist  
Cuenca, Ecuador
