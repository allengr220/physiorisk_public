# Public pipeline fix status

## Status: completed in Sprint 3C

The previously proposed notebook repair has been implemented without running notebooks or editing scientific code.

## Notebook 02 replacement

- **Previous source:** `benchmark_dataset_builder_PRscore.ipynb`
- **Previous SHA256:** `c85cd43c9cc8bcd159bdc5f987fc5370581eb8673bea529bacd8f772ce540a6f`
- **Replacement source:** `/home/ubuntu2204/cognitive-ledger/longevity/notebooks/benchmark_levine_no_crp_cohort_builder.ipynb`
- **Installed destination:** `notebooks/02_benchmark_dataset_builder.ipynb`
- **Installed SHA256:** `612a52cb8d585bc48a5629cf35c26d469d378f6cf9b0e15b6251f364b978c103`
- **Verification:** destination is byte-identical to the recovered archive source and explicitly writes `benchmark_levine_no_crp_cohort.parquet`.

## Scoring notebook insertion/renumbering

- `notebooks/04_physiorisk_scoring.ipynb` was already correctly installed by Sprint 3.
- It remains byte-identical to `physiorisk_canonical_frozen_baseline_notebook_levinenocrp.ipynb` at SHA256 `61100d7f1a9adc130a7781ae0012cc3d88fab93f1e48729085442781f7308a59`.
- Validation, figures, and optional ablation remain numbered 05, 06, and 07 respectively.

## Validation duplicate resolution

- The repository root no longer contained the top-level notebook at Sprint 3C inspection time.
- Its more complete content was already present as an unstaged modification in `notebooks/05_physiorisk_model_validation.ipynb` and was preserved.
- The numbered notebook reads both scored parquets, writes `physiorisk_vs_phenoage_aligned_comparison.csv`, and explicitly writes `test_phenoage_compare_outputs.parquet`.
- The remaining untracked Windows `Zone.Identifier` sidecar was removed; it contained no notebook content.

## Top-level duplicate cleanup

- No top-level `.ipynb` file remains.
- All required canonical content is preserved under `notebooks/`.
- No unresolved duplicate required `docs/SPRINT3C_UNRESOLVED.md`.

## Documentation/manifest repair

- The notebook 01 → 02 → 03 producer chain is documented as resolved.
- Notebook 05 is documented as producer of both aggregate and row-level comparison artifacts.
- `data/ARTIFACT_MANIFEST.tsv` and `docs/EXPECTED_ARTIFACTS.md` distinguish committed, public-source-regenerable, and external Google Drive/MyDrive artifacts.
- Current manuscript terminology is mapped to frozen legacy identifiers without renaming data columns.

## Remaining external artifacts

Large canonical datasets, frozen baseline train/test parquets, the exact DemoRisk pickle/metadata, scoring metadata CSVs, comparison CSV, and row-level comparator parquet remain outside Git. Their expected MyDrive paths and producer notebooks are documented. Three participant-level parquets have hash-verified WSL copies outside the repository.

## Remaining ambiguities

- No exact standalone producer/export was identified for manuscript Table 1; the table remains embedded in the committed manuscript.
- The optional notebook 07 is an older v1/v2/v3 ablation branch, not a direct ablation of the submitted two-axis model.
- External artifact presence in Google Drive/MyDrive was not independently enumerated from WSL during this sprint.

These issues do not break the direct notebook 01–06 producer graph. The repaired pipeline classification is `PASS_WITH_EXTERNAL_ARTIFACTS`.
