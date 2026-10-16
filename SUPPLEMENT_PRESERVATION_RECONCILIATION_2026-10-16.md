# Supplement preservation reconciliation — 2026-10-16

## Sources and outputs

Preservation authority: `submission/biogerontology/PhysioRisk_Biogerontology_Supplementary_Material.pdf` (11 pages; SHA-256 `7d3949fa55643e89e8a7f8f7d2c7ea59b638f41cf0c542831d32eac60aa892d4`). Its table structure matches the historical editable source `manuscript/PhysioRisk_RS_Supplementary_Material.docx` (SHA-256 `44d31b169530598335f7a96ca7e101c91b29b8867388683a0104f1544f53e65d`), except that the PDF title page contains additional submission metadata. The prior scientifically corrected DOCX supplied the approved Supplementary Methods and S5 table.

New files: `submission/biogerontology/PhysioRisk_Biogerontology_Supplementary_Material_corrected_preserved_2026-10-16.docx` and `.pdf` (10 pages). The mechanical rebuild is `scripts/preserve_biogerontology_supplement_2026_10_16.py`. Frozen numerical sources are in `outputs/physiorisk_v2_validation/`.

## Exhaustive delta classification against the submitted PDF

Category **A** is an approved scientific/content change under Changes 20–26 or 30–33. Category **B** is mechanically required to implement or faithfully document A. Category **C** is unauthorized. No C differences remain.

| Original element | Difference in new supplement | Class |
| --- | --- | --- |
| Title page | None against the submitted PDF: journal, author, affiliation, corresponding-author line, email, and the canonical-artifacts sentence are present in their original order. The editable source omitted four metadata lines; restoring them from the PDF was necessary to preserve the submitted title page. | B relative to editable source; no PDF delta |
| Supplementary Methods | Added the approved harmonization statement, PhenoAge NCP equation and unit contract, CRP omission, linear glucose statement, and cycle-specific glucose handling. The entire Methods XML is identical to the prior corrected DOCX. | A (30–32) |
| S1 | Original eight-column headers, contrast labels, cohort labels, replicate count, seed, note, and table layout are restored. Only the three ΔC estimates, their six interval limits, and three bootstrap proportions changed to `paired_cindex_bootstrap_v2.csv` values. | A (20) |
| S1 provenance | Original line location and style retained; historical artifact path replaced with `paired_cindex_bootstrap_v2.csv`. | B |
| S2 | Original 11-column headers, metadata fields, note, and table layout restored. DemoRisk remains numerically the same; the PhysioRisk and CalibratedTotalRisk diagnostics and their residual summaries changed to frozen values. The two historical axis rows were removed, and PhenoAge NCP and acceleration rows were added from `ph_diagnostics_v2.csv`. All five rows carry the frozen statistic, p value, flag, warning, and regional summary. | A (21) |
| S2 provenance | Original line location and style retained; historical artifact path replaced with `ph_diagnostics_v2.csv`. | B |
| S3 | DemoRisk and PhysioRisk rows removed. The CalibratedTotalRisk row retains original stable design metadata and column labels; its log HR at 60 months, HRs at 12/60/96 months, coefficient, interval limits, p value, and direction come directly from frozen fields in `time_interactions_v2.csv`. The original e-fold multiplier column was omitted because no frozen field supplies it. The original diagnostic note has one approved flag sentence appended. | A (22); B for omission of unsupported multiplier |
| S3 provenance | Original line location and style retained; historical artifact path replaced with `time_interactions_v2.csv`. | B |
| S4 | Original 14-column, two-horizon row layout, headers, note, and `True` no-recalibration field restored. Development baseline survival, predicted/observed mortality, difference, O/E, global slope and its CI, horizon intercept/slope, Brier score, and usable N changed to `fixed_horizon_calibration_v2.csv` values at specified display precision. No horizon-specific slope CIs were added. | A (23) |
| S4 provenance | Original line location and style retained; historical artifact path replaced with `fixed_horizon_calibration_v2.csv`. | B |
| S5 | The approved five-score × four-metric replacement table and its note are byte-identical at XML element level to the prior corrected DOCX. This differs from the submitted nine-column S5 under approved Change 24. | A (24) |
| S5 provenance | Table-specific line restored in its original position, pointing to `censoring_robust_discrimination_v2.csv`. | B |
| S6–S7 | No content, caption, table, note, provenance, structure, or pagination change. Their four-element sections are canonical-XML-identical to the editable source. PDF page images 7–9 are pixel-identical to the submitted PDF images at the same rendering settings. | No delta |
| S8 | Original nine-column headers, repository-style analysis/cohort labels, score labels, complete-case missing-data wording, note structure, and table layout restored. C-index and age-correlation fields changed to frozen primary validation values. Two obsolete imputation/extension claims were removed from the rule and Status cells; the approved extension rationale appears in the note. The no-op finding remains. | A (25) |
| S8 provenance | Original line location and style retained; historical artifact path replaced with `primary_validation_metrics_v2.csv`. The no-op observation is preserved from the original supplement and the approved corrected manuscript; no new statistic was inferred. | B |
| S9 | Historical reader-facing table, note, and provenance removed; S10 not created. | A (26) |
| Pagination | The Methods insertion and S9 removal account for the 10-page output versus the 11-page submitted PDF. S6/S7 still occupy the same three page images. | B |

The provenance path changes are the only repository-style text changes outside approved scientific content. No original provenance line was deleted, and no obsolete path was restored.

## Required confirmations and QA

- Title metadata restored; the canonical-artifacts sentence is verbatim.
- Supplementary Methods are canonical-XML-identical to the prior corrected version.
- S1 has eight original columns and all frozen corrected values, including proportions `1.0000`, `0.4775`, and `0.8205`.
- S2 has 11 original columns and only five primary scores.
- S3 retains all frozen time-specific HR fields without calculation; only the unsupported e-fold multiplier field was omitted. Its interaction coefficient is `0.12970`, CI `0.02929–0.23011`, p=`0.01135`, with p<0.01 flag No in the note.
- S4 has 14 original columns and two horizon rows. Its values match the frozen calibration CSV after display rounding; no horizon-specific slope intervals were invented.
- S5's approved replacement table and note were retained without modification.
- S6 and S7 are structurally identical to the historical editable source and visually identical to the submitted PDF pages.
- S8 has nine original columns and only the approved score/value/rationale changes.
- S9 and S10 are absent. No repair, debugging, or correction-history narrative appears in the supplement.
- DOCX package CRC passes. The PDF rendered successfully. All 10 pages were inspected against the submitted PDF and prior corrected supplement; no clipping, broken symbols, table overflow, or caption displacement was found.
- The submitted PDF, historical editable DOCX, prior corrected supplement, frozen artifacts, and main manuscript were not modified. Main manuscript SHA-256 remains `840ee077e17d8d8d66063b8ba841510ec4ae2565b3418efb841a8d42afc273b3`.
- No commit or push was made.

**Category C count: 0.** No field required a guessed or newly calculated value.
