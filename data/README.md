# Data and derived artifacts

This directory intentionally contains documentation only. Raw NHANES data, mortality-linkage inputs, participant-level analytic datasets, model parquets, and other large derived artifacts are not committed to Git.

`ARTIFACT_MANIFEST.tsv` records the expected location, producer, consumers, role, storage status, and provenance status of every major pipeline artifact. Paths beginning with `$MYDRIVE` correspond to `/content/drive/MyDrive` in Google Colab. Repository-relative `data/...` paths are supported by supplemental local scripts where documented; the manifest does not claim that an external artifact is present locally.

Three derived artifacts have hash-verified WSL copies outside the repository:

- `benchmark_levine_no_crp_cohort.parquet`
- `physiorisk_2axis_v1_train_scored_from_frozen_baseline_levinenocrp.parquet`
- `physiorisk_2axis_v1_test_scored_from_frozen_baseline_levinenocrp.parquet`

Their hashes and row/event counts are documented in `docs/ARTIFACT_PROVENANCE.md`. Do not add data files here without a deliberate data-release and privacy review.

| Manuscript term | Legacy code/data identifier |
|---|---|
| DemoRisk | `BaselineRisk` |
| PhysioRisk | `PhysioRisk_2axis` |
| TotalRisk | `TotalRisk_2axis` |
| PhenoAge NCP | `PhenoAge_noCRP_proxy` |
| PhenoAge NCP acceleration | `PhenoAgeAccel` |
