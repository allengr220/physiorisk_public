# Project status

## Manuscript status

- Manuscript title: *PhysioRisk: an interpretable survival-modeling framework for separating demographic and physiological mortality risk*
- Journal status: rejected after external peer review by *BMC Medical Informatics and Decision Making*
- Preprint: Research Square Version 2 posted 2026-10-06: https://www.researchsquare.com/article/rs-9829732/v2
- Research Square v2 DOI: https://doi.org/10.21203/rs.3.rs-9829732/v2
- Historical Research Square v1 DOI: https://doi.org/10.21203/rs.3.rs-9829732/v1

## Repository status

Repository consolidation, reviewer-response analyses, and public-snapshot sanitization are complete. The repository is an auditable reproducibility record, but is not a self-contained data bundle: participant-level artifacts remain external and frozen historical notebooks retain documented environment-specific paths.

Completed:
- Canonical notebooks renamed into dependency order
- Core project documentation scaffolded
- Model specification frozen
- Validation and diagnostic table outputs committed
- Artifact provenance, pipeline audit, dependency graph, and reviewer-readiness documents added
- Revised terminology adopted: DemoRisk, PhysioRisk, CalibratedTotalRisk, PhenoAge NCP, and PhenoAge NCP acceleration
- Notebook execution outputs stripped and event-level Schoenfeld residual records excluded from the public snapshot

The repository corresponds to the substantially revised Research Square v2 analysis and manuscript package. Validation reported here is internal temporal validation; external independent validation remains outstanding.

Remaining release action:
- Obtain release-owner approval for the final repository-visibility change. Do not change visibility as part of this release-metadata update.

## Release principle

Scientific results, analysis logic, model coefficients, aggregate tables, and manuscript numerical values are preserved in the public-release preparation.

## 2026-08-23 — Sprint 3C completed

Commit: 5546635

Completed public-pipeline provenance repair. Notebook 02 was replaced with the recovered no-CRP cohort builder. Notebook 04 is confirmed as the scored PhysioRisk parquet producer. Notebook 05 now explicitly exports both `test_phenoage_compare_outputs.parquet` and the aggregate comparison CSV. Top-level duplicate notebooks were removed. Pipeline audit result is `PASS_WITH_EXTERNAL_ARTIFACTS`.

No datasets, model binaries, or raw NHANES files were committed. Remaining provenance gaps are standalone Table 1 and the optional ablation branch.
