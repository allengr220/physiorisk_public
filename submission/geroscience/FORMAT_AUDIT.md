# GeroScience format audit — finalized PhysioRisk package

Audit date: 2026-10-07

Scope: strict mechanical implementation of author-approved changes. The frozen Research Square v2 manuscript remained the scientific source. No unapproved scientific, numerical, citation, reference, table, figure, equation, Methods, Results, Discussion, Limitations, or Conclusions changes were made.

Requirements source: [GeroScience Submission Guidelines](https://link.springer.com/journal/11357/submission-guidelines), accessed 2026-10-07.

## Audit results

| Item | Classification | Result |
|---|---|---|
| Article type suitability | PASS | Original research structure and subject scope remain suitable. |
| Title page | FORMAT FIX APPLIED | Added exactly: “Corresponding author: Gregory S. Allen” and “Email: allengr220@gmail.com”. The existing author name and affiliation were preserved verbatim. |
| Abstract | USER INPUT REQUIRED | Replaced with the exact author-approved abstract. Final count is **252 words excluding the four structured labels** (256 including Background, Methods, Results, and Conclusions). GeroScience requests 150–250 words, so the approved text is two words above the stated maximum. It was not independently shortened. |
| Keywords | FORMAT FIX APPLIED | Replaced with exactly six approved keywords: mortality prediction; survival analysis; physiological aging; biomarkers; NHANES; risk decomposition. |
| Manuscript file type | PASS | Valid `.docx` file. |
| Font, spacing, and margins | PASS | Existing mechanical formatting was preserved. |
| Page numbering | FORMAT FIX APPLIED | The previously applied blank first-page footer remains in place. Pages 2–13 use automatic page numbering. |
| References and citations | PASS | Reference text, order, numbering, and all citations are unchanged. |
| Tables | PASS | Both native Word tables and every cell value are unchanged. |
| Manuscript assembly order | ACCEPTABLE FOR INITIAL SUBMISSION | References/tables/figures were not reorganized. GeroScience states that initial Original Research Article submissions may be considered without complete house-style formatting. |
| Figure legends | ACCEPTABLE FOR INITIAL SUBMISSION | Frozen legends are unchanged. House-style conversion from “Figure” to “Fig.” and related punctuation can be handled later if requested. |
| Standalone figures | PRODUCTION-STAGE ISSUE | `Fig1.pdf` and `Fig2.pdf` are unchanged and retain the exact canonical PNG pixels without interpolation. Their source metadata are approximately 200 ppi, below the journal’s recommendations for bitmap line/combination art. Canonical SVG candidates exist, but an exactly appearance-preserving match to the frozen PNG artwork has not been established; they were not substituted. Figure 2’s internal title was retained exactly as instructed. |
| Equations | PRODUCTION-STAGE ISSUE | The seven displayed equations remain styled Cambria Math text, not native OMML. Their characters, subscripts, operators, minus signs, arrows, multiplication sign, Greek letters, and combining hat are unchanged. They can be converted at production stage if requested and author-verified. |
| Supplement identification | FORMAT FIX APPLIED | Added the exact approved identification block to page 1: article title, GeroScience, author, affiliation, corresponding-author line, and email. |
| Supplement scientific content | PASS | Supplementary Tables S1–S9, captions, notes, values, ordering, and provenance lines are unchanged. Rendered pages 2–11 are pixel-identical to the prior frozen supplementary PDF. |
| Statements and Declarations | FORMAT FIX APPLIED | Replaced the former declaration block with one nonduplicated “Statements and Declarations” block containing the exact approved Funding, Ethics approval and consent to participate, Consent for publication, Competing interests, Author contributions, Data and code availability, Use of generative AI, and Preprint statements. |
| Ethics wording | FORMAT FIX APPLIED | Inserted the exact author-approved wording specifying written informed consent and secondary analysis of de-identified public-use data. |
| Data and code availability | FORMAT FIX APPLIED | Replaced with the exact approved statement. The URL appears exactly once as `https://github.com/allengr220/physiorisk_public/`. |
| Preprint disclosure | FORMAT FIX APPLIED | Added the exact approved Research Square Version 2 disclosure. DOI appears exactly once as `10.21203/rs.3.rs-9829732/v2`. |
| Author information | FORMAT FIX APPLIED | Corresponding-author name and email were added exactly as approved. |
| ORCID | ACCEPTABLE FOR INITIAL SUBMISSION | No ORCID was supplied. GeroScience requests an ORCID only if available. None was inferred or added. |

## Exact approved textual changes

1. Replaced the four abstract paragraphs with the supplied approved text.
2. Replaced the keyword line with the supplied six-keyword line.
3. Added two title-page lines:
   - `Corresponding author: Gregory S. Allen`
   - `Email: allengr220@gmail.com`
4. Replaced `Declarations` and its former subsections with one `Statements and Declarations` block using the eight supplied headings and statements, in the supplied order.
5. Updated only the supplementary front matter with the supplied identification block.

No other manuscript wording was changed.

## Exact-string verification

- Approved abstract: exact four-paragraph match.
- Keywords: exact match; count = 6.
- Corresponding author: exact match.
- Email: `allengr220@gmail.com` — present exactly once.
- GitHub URL: `https://github.com/allengr220/physiorisk_public/` — present exactly once.
- Research Square DOI: `10.21203/rs.3.rs-9829732/v2` — present exactly once.
- `Statements and Declarations` heading — present exactly once.
- Each approved declaration heading and statement — exact match and present once.
- No duplicate former declaration sections remain.

## Unapproved-region validation

- The complete XML element sequence from `Introduction` through the end of `Conclusions` is exactly unchanged: 108 elements before and after.
- The complete XML element sequence from `Tables and figures` through the end of `References` is exactly unchanged: 38 elements before and after.
- All DOCX package parts other than `word/document.xml` are byte-identical to the pre-change GeroScience derivative.
- Equations: 7 before and after; formula text and run formatting unchanged.
- Embedded manuscript figures and external `Fig1.pdf`/`Fig2.pdf` are unchanged.
- Because the protected manuscript regions are XML-identical, there were no accidental changes to scientific numbers, citations, references, table contents, figure legends, special characters, superscripts/subscripts, minus signs, en dashes, or multiplication signs outside the explicitly approved replacements.

## Supplement validation

- The front matter contains the exact approved seven-line identification block.
- The source DOCX element sequence from Supplementary Table S1 through Supplementary Table S9 is semantically XML-identical before and after.
- The final supplement contains 11 landscape pages.
- Rendered pages 2–11 have no differing pixels compared with the prior frozen supplementary PDF.
- Only page 1 differs, within the identification-block region.

## Render validation

- Manuscript: 13 US-Letter pages rendered and visually inspected page by page.
- Supplement: 11 landscape pages rendered and visually inspected page by page.
- Title page, abstract, contact block, declarations, tables, equations, embedded figures, legends, and references are visible and intact.
- No clipping, overlapping text, missing pages, blank scientific pages, corrupted glyphs, or duplicated declaration sections were found.

## Remaining issues

- **USER INPUT REQUIRED:** the exact approved abstract is 252 words excluding labels, two words above the journal’s 250-word maximum. No reduction is authorized in this pass.
- **PRODUCTION-STAGE ISSUE:** equations remain styled mathematical text rather than OMML.
- **PRODUCTION-STAGE ISSUE:** figure raster resolution is below the journal’s stated line/combination-art recommendations; no appearance-preserving replacement was authorized or substituted.
- **ACCEPTABLE FOR INITIAL SUBMISSION:** house-style figure-legend punctuation and final manuscript block ordering remain unchanged.

## Overall result

**PASS WITH ISSUES** — all author-approved changes were applied exactly, protected manuscript and supplementary content remained unchanged, and the only unresolved author decision is the 252-word abstract relative to the journal’s 250-word limit.
