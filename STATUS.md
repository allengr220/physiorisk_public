# Project status

## Manuscript status

- Manuscript title: *PhysioRisk: an interpretable survival-modeling framework for separating demographic and physiological mortality risk*
- Journal status: rejected after external review by *BMC Medical Informatics and Decision Making*
- Preprint: posted on Research Square
- DOI: [insert DOI]

## Repository status

Sprint 3 repository consolidation and reviewer-gap assessment are complete. The repository is an auditable public record, but is not yet a self-contained, end-to-end reproducibility package because required data/model artifacts and upstream producer alignment remain unresolved.

Completed:
- Canonical notebooks renamed into dependency order
- Core project documentation scaffolded
- Model specification frozen
- Validation and diagnostic table outputs committed
- Artifact provenance, pipeline audit, dependency graph, and reviewer-readiness documents added

Pending:
- Insert final Research Square DOI in README, STATUS, CITATION, and manuscript references
- Inventory/export the external Google Drive/MyDrive artifacts and record hashes
- Publicly provision or reproducibly build the no-CRP benchmark and frozen baseline/model artifacts
- Replace private Colab paths with a documented public data-location mechanism in a future reproducibility sprint
- Add exact frozen residualization, axis-standardization, and physiology-model parameters
- Push repository to GitHub

## Release principle

The submitted manuscript and model remain frozen during repository consolidation. Scientific revisions and new analyses require a separate sprint.
## 2026-08-23 — Sprint 3C completed

Commit: 5546635

Completed public-pipeline provenance repair. Notebook 02 was replaced with the recovered no-CRP cohort builder. Notebook 04 is confirmed as the scored PhysioRisk parquet producer. Notebook 05 now explicitly exports both `test_phenoage_compare_outputs.parquet` and the aggregate comparison CSV. Top-level duplicate notebooks were removed. Pipeline audit result is `PASS_WITH_EXTERNAL_ARTIFACTS`.

No datasets, model binaries, or raw NHANES files were committed. Remaining provenance gaps are standalone Table 1 and the optional ablation branch.
