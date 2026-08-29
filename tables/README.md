# Tables

This directory contains manuscript-linked and post-review diagnostic outputs for PhysioRisk.

Current status:
- Submitted benchmark outputs were generated in Colab/notebook workflows and are not all committed.
- Sprint 1/2 reconstruction, validation, calibration, cohort, and sensitivity CSVs are committed here.
- `notebooks/08_validation_v2.ipynb` and `notebooks/09_cohort_comparator_sensitivity.ipynb` display Sprint 2 outputs.
- Sprint 3D replaced the retained-benchmark-only cohort tables with upstream versions produced by `scripts/run_s3d_cohort_regeneration.py` from the regenerated 53,255-person mortality-eligible population.
- `physiorisk_vs_phenoage_aligned_comparison.csv` was re-exported by `scripts/run_s3d_table2_export.py`, which executes the canonical comparison cells from notebook 05. Its input hashes and submitted-rounding checks are in the adjacent metadata JSON.
- `s3d_nhanes_input_manifest.csv` records URLs, hashes, byte sizes, and row counts for all successful public inputs used in the targeted rebuild; `s3d_regeneration_manifest.json` records staged output hashes.

See `docs/ARTIFACT_PROVENANCE.md` for per-file lineage and status.
