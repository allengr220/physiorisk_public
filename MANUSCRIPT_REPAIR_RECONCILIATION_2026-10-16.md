# Biogerontology submission reconciliation — 2026-10-16

## Inputs and frozen numerical authority

- Authoritative manuscript baseline: `submission/biogerontology/PhysioRisk_Biogerontology_Manuscript_corrected_working_2026-10-16(1).docx` (SHA-256 `1dc4964b8559bb2b13e4da30b2fc66b3d5ab08f59ed9887c62923099b52b32cc`).
- Submitted supplement reference: `submission/biogerontology/PhysioRisk_Biogerontology_Supplementary_Material.pdf` (SHA-256 `7d3949fa55643e89e8a7f8f7d2c7ea59b638f41cf0c542831d32eac60aa892d4`).
- Editable supplement source: `manuscript/PhysioRisk_RS_Supplementary_Material.docx` (SHA-256 `44d31b169530598335f7a96ca7e101c91b29b8867388683a0104f1544f53e65d`). It contains the corresponding S1–S9 table sequence and was used as the document/layout source. The submitted PDF was retained as a read-only reference.
- Frozen validation directory: `outputs/physiorisk_v2_validation/`. The named required files `calibration_plot_data_v2.csv`, `paired_cindex_bootstrap_v2.csv`, and `historical_corrected_comparison_v2.csv` were all present before any modification.
- Additional frozen files used for reconciliation: `fixed_horizon_calibration_v2.csv`, `ph_diagnostics_v2.csv`, `time_interactions_v2.csv`, `censoring_robust_discrimination_v2.csv`, `primary_validation_metrics_v2.csv`, `calibrated_totalrisk_v2_coefficients.csv`, `validation_metadata_v2.json`, and `artifact_manifest_v2.json`.

## New outputs and mechanical construction

- `submission/biogerontology/PhysioRisk_Biogerontology_Manuscript_corrected_complete_2026-10-16.docx` and `.pdf` (13 PDF pages).
- `submission/biogerontology/PhysioRisk_Biogerontology_Supplementary_Material_corrected_2026-10-16.docx` and `.pdf` (10 PDF pages).
- Rebuild code: `scripts/rebuild_biogerontology_2026_10_16.py`.

Figure 2 was plotted directly from all 20 decile rows in `calibration_plot_data_v2.csv` (10 at 60 months and 10 at 96 months). The code uses the frozen mean predicted mortality and Kaplan–Meier observed mortality columns as x and y coordinates. No decile point was inferred from aggregate statistics. The existing placeholder was replaced by changing only `word/media/image3.png` in the manuscript DOCX. `word/document.xml`, Figure 1's image, and all other manuscript package entries remained byte-identical to the authoritative working baseline. The Figure 2 caption is unchanged and occurs once.

## Supplement changes

| Table | Reconciliation |
| --- | --- |
| S1 | Three paired contrasts and percentile intervals match `paired_cindex_bootstrap_v2.csv` at five decimal places. The bootstrap proportions above zero come **exactly** from that file's `proportion_bootstrap_delta_above_zero` column: `1.0000`, `0.4775`, and `0.8205`, in table order. Each contrast has 2,000 completed replicates and seed 20260821. |
| S2 | Five primary score-level Schoenfeld rows only, from `ph_diagnostics_v2.csv`; the two historical axis rows were removed. Values and p<0.01 flags match the approved ledger. |
| S3 | CalibratedTotalRisk interaction only, from `time_interactions_v2.csv`: 0.12970 (0.02929–0.23011), p=0.01135, p<0.01 flag No. No time-specific derived HRs were added. |
| S4 | Five- and eight-year calibration values, usable N, and global Cox slope match `fixed_horizon_calibration_v2.csv` after display rounding. No confidence intervals were invented for horizon-specific slopes. |
| S5 | Five scores × four horizon-specific discrimination values match `censoring_robust_discrimination_v2.csv` after display rounding. |
| S6–S7 | Captions, tables, notes, and provenance paragraphs were carried forward unchanged. Canonical XML of each four-element section is identical to the editable source. |
| S8 | C-indices and age correlations match `primary_validation_metrics_v2.csv`; the frozen retained-cohort observation that imputation changed no values is retained. The excluded-participant rationale is the approved missing-data/design wording. |
| S9–S10 | Neither appears in the new reader-facing supplement. No replacement historical table was created. |

Supplementary Methods now contain the specified PhenoAge NCP equation, unit contract, cross-cycle harmonization statement, and cycle-specific glucose handling. S6 is a preselection missingness table, not a score source-variable table, so it remained unchanged.

## Manuscript QA

The authoritative baseline already contained the approved laboratory harmonization, missing-data rationale, coefficients (PhysioRisk 0.419/0.239; CalibratedTotalRisk 1.0650/0.3610), PhenoAge NCP units, IPCW wording, primary score C-indices/HRs/age correlations, fixed-horizon calibration, proportional-hazards interpretation, censoring-robust results, model-development limitation, and clean Table 1 caption. It retains the Research Square Version 2 citation pending the factual Version 3 update. The manuscript text was not edited.

The detailed ledger's CalibratedTotalRisk − DemoRisk contrast is 0.01762 (0.01197–0.02366), matching `paired_cindex_bootstrap_v2.csv`. The manuscript's 0.0176 (0.0120–0.0237) is ordinary four-decimal manuscript-level rounding of those three numbers, consistent with its surrounding Results precision. No manuscript precision change was needed.

No unsupported claim of similar HR gradients, forensic phrase, or prohibited full-precision sentence was found. The manuscript retains genuine scientific limitations, including strict proportional-hazards nonconformity and the limited eight-year tail. Figure 1 is unchanged. The new Figure 2 image is 220 dpi at its generated size and renders clearly on page 12.

## Structural, numerical, and rendered QA

- Both DOCX files passed ZIP/package CRC checks. The final manuscript has the same 21 package entries as its source; the supplement has the same 20 entries as its editable source.
- Both PDFs rendered through LibreOffice. All 13 manuscript and all 10 supplement pages were inspected as page images. No clipped text, table overflow, missing image, misplaced caption, broken equation/minus sign, malformed reference, or unexpected page break was observed. S6 spans two pages with its column header repeated; its rows remain intact. The source supplement's table-per-page layout was retained.
- Automated assertions checked S1–S5 and S8 display values, Methods units/formula terms, absence of S9/S10, manuscript caption and rounded ΔC, and absence of stale phrases. All passed.
- Search found no `historical_submitted_not_current`, obsolete residualization-parameter rationale, Figure 2 placeholder text, `preserved final path`, or prohibited full-precision sentence in the new reader-facing DOCX text.
- No contradiction between a required frozen artifact and the approved ledger was found. No unresolved issue requiring scientific judgment remains.

## Repository state and source preservation

Before work, `git status --short` contained only these untracked pre-existing files:

```text
?? submission/biogerontology/PhysioRisk_Biogerontology_Manuscript_corrected_working_2026-10-16(1).docx
?? submission/biogerontology/PhysioRisk_Biogerontology_Manuscript_corrected_working_2026-10-16.docx:Zone.Identifier
```

After work, those two entries remain untracked; the only additional entries are the four version-qualified submission outputs, this report, and the rebuild script. `git diff --stat` and `git diff --check` show no tracked-file changes. The historical submitted manuscript and supplement, the editable source supplement, and all frozen artifacts were read only. No commit or push was made.
