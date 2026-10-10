# Biogerontology Springer Nature Snapp format audit

Audit date: 2026-10-09

Overall result: **PASS**

Scope: strict journal-format conversion of the completed GeroScience manuscript followed by Snapp-specific figure preparation. Scientific prose, claims, analyses, numerical values, abstract, keywords, ethics wording, AI disclosure, tables, equations, figure content, and figure captions were frozen. The only Snapp-stage manuscript prose change is the explicitly approved replacement of the Data and code availability paragraph. Earlier Biogerontology-stage text changes remain limited to numeric citation strings converted to author-year citation strings and mechanical reference-list style/order changes.

Requirements checked against the current [Biogerontology submission guidelines](https://link.springer.com/journal/10522/submission-guidelines) and the official [STROBE cohort-study checklist](https://www.strobe-statement.org/checklists/), accessed 2026-10-09.

## Files created

- `PhysioRisk_Biogerontology_Manuscript.docx`
- `PhysioRisk_Biogerontology_Supplementary_Material.pdf`
- `Fig1.png`
- `Fig2.png`
- `Fig1.pdf`
- `Fig2.pdf`
- `STROBE_Checklist.pdf`
- `FORMAT_AUDIT.md`

No cover-letter changes were made during Snapp preparation.

## Requirement audit

| Item | Classification | Result |
|---|---|---|
| Article type | PASS | Package is for **RESEARCH**. It is not labelled or framed as Methodology. |
| Editable Word source | PASS | Manuscript is a valid `.docx`; the Snapp-stage package comparison found changes only in `word/document.xml` and the two embedded PNG media parts. |
| Title page | PASS | Frozen title, author, affiliation, corresponding-author line, and email are present exactly. |
| Corresponding-author email | PASS | `allengr220@gmail.com` is present exactly. |
| Abstract | PASS | Approved abstract is unchanged. Count = **246 words excluding the four structured labels**, using the approved token convention that counts punctuation-separated numeric components/year ranges separately. It is within the journal's 150–250-word limit. |
| Keywords | PASS | Exactly six, unchanged: mortality prediction; survival analysis; physiological aging; biomarkers; NHANES; risk decomposition. |
| In-text citations | FORMAT FIX APPLIED | All 30 numeric citation points were converted mechanically to author-year form using only the frozen 24-item reference list. Zero numeric bracket citations remain. |
| Reference list | FORMAT FIX APPLIED | 24 references before and after. Entries were mechanically converted to Springer author-year form and alphabetized by first-author surname. No work was added or removed. |
| Reference 13 date | FORMAT FIX APPLIED | Updated from `n.d.` to **2022** based on the official CDC document `Public-use Linked Mortality Files`, updated May 2022. The supported scientific claim is unchanged. |
| Tables and captions | PASS | Two native Word tables, all cells, and both frozen table captions are XML-identical. |
| Figures and captions | PASS | The two embedded figures were replaced in place with the Snapp-compliant direct PNG exports. Both frozen captions are byte-for-byte unchanged. |
| Figure technical specifications | PASS | Canonical dimensions before the Snapp export were exactly **1800×1120 px** for Figure 1 and **1920×860 px** for Figure 2. Direct 3× logical-scale exports are exactly **2700×1680 px** and **2880×1290 px**, respectively, satisfying the 1500×1200-pixel minimum. The files are losslessly compressed RGB PNGs; no existing raster was interpolated or enlarged. |
| Figure appearance validation | PASS | The canonical drawing workflow was parameterized without changing its default 2× output. Control re-renders at 2× were RGB-pixel-identical to both canonical PNGs (zero changed pixels). The final 3× files use the same coordinates, proportions, colors, labels, fonts, line placement, data, and content. The rendered DOCX figures were visually inspected at their existing locations. |
| Vector alternative | NOT SUBSTITUTED | The workflow emits SVG candidates, but they are not appearance-identical to the canonical PNG renderer: SVG font selection/metrics and some drawing details differ, and the Figure 2 SVG includes a rotated y-axis label absent from the canonical PNG. No SVG or EPS is therefore reported as a faithful Snapp alternative. |
| Equations | PRODUCTION-STAGE ISSUE | All seven displayed equations are semantically and XML-identical to the source and remain Cambria Math styled text, not native OMML. Springer may request Equation Editor/MathType conversion at production. |
| Statements and Declarations | PASS | Only the explicitly approved Data and code availability paragraph was replaced. Funding, ethics/consent, consent for publication, competing interests, author contributions, AI disclosure, and preprint disclosure are unchanged. |
| Ethics and informed consent | PASS | Frozen NCHS ethics-review and written-informed-consent wording is unchanged in Methods and Declarations. |
| AI disclosure in Methods | PASS | The frozen disclosure remains under `Methods → Use of generative AI`; its identical declaration copy also remains unchanged. This satisfies the journal's location request without editing approved wording. |
| Supplementary PDF identification | FORMAT FIX APPLIED | Only the journal identifier on page 1 changed from `GeroScience` to `Biogerontology`. Title, author, affiliation, corresponding-author line, and email remain present. |
| Supplementary tables S1–S9 | PASS | The rendered source and target each yielded 1,048 ordered paragraph fragments. After normalizing the one journal-name substitution, the sequences are exactly identical. S1–S9 content, captions, values, order, notes, and provenance lines are unchanged. |
| STROBE checklist | FORMAT FIX APPLIED | Completed official cohort-study checklist supplied as a two-page landscape PDF. Each applicable item maps to an actual manuscript section/paragraph; gaps and non-applicable items are marked without adding manuscript content. |
| Preprint disclosure | PASS | Frozen Research Square Version 2 disclosure and DOI are unchanged. |
| Supplement naming convention | ACCEPTABLE FOR INITIAL SUBMISSION | The requested filename is retained. The journal describes online resources using `Online Resource`/`ESM` nomenclature; the submission system may relabel the file. |

## Exact manuscript changes

1. Converted 30 bracketed numeric citation points in 20 body paragraphs to author-year form.
2. Removed numeric prefixes from the 24 references, moved years into Springer author-year position, made mechanical punctuation/journal-style adjustments, and alphabetized the entries.
3. Updated the year for reference 13 and its corresponding in-text citation from `n.d.` to `2022`, based on the official CDC document `Public-use Linked Mortality Files`, updated May 2022. No other bibliographic content or supported scientific claim changed.
4. For the Snapp package, replaced only the existing Data and code availability paragraph with the user-approved text.
5. Replaced only the two embedded canonical PNG media payloads with direct high-resolution exports; their drawing extents and captions were not changed.

No other manuscript wording changed. Relative to the pre-Snapp Biogerontology DOCX, all package members are byte-identical except `word/document.xml`, `word/media/image1.png`, and `word/media/image2.png`. Replacing the approved new paragraph with the former paragraph makes `word/document.xml` byte-identical to its pre-Snapp version.

## Citation and reference mapping

| Old reference number | Author-year citation | Alphabetized position |
|---:|---|---:|
| 1 | Lu et al. 2019 | 17 |
| 2 | Ferrucci et al. 2018 | 8 |
| 3 | Klemera and Doubal 2006 | 15 |
| 4 | Liu et al. 2018 | 16 |
| 5 | Cohen et al. 2013 | 2 |
| 6 | Milot et al. 2014 | 18 |
| 7 | Cohen et al. 2015 | 3 |
| 8 | Vaupel et al. 1979 | 24 |
| 9 | Duchateau and Janssen 2007 | 7 |
| 10 | Rockwood and Mitnitski 2007 | 21 |
| 11 | Collins et al. 2015 | 4 |
| 12 | National Center for Health Statistics 1999–2016 | 19 |
| 13 | National Center for Health Statistics 2022 | 20 |
| 14 | Cox 1972 | 5 |
| 15 | Kleinbaum and Klein 2012 | 14 |
| 16 | Hartman et al. 2023 | 12 |
| 17 | Bewick et al. 2004 | 1 |
| 18 | Harrell et al. 1996 | 11 |
| 19 | Grambsch and Therneau 1994 | 10 |
| 20 | Crowson et al. 2016 | 6 |
| 21 | Royston 2014 | 22 |
| 22 | Graf et al. 1999 | 9 |
| 23 | Uno et al. 2011 | 23 |
| 24 | Heagerty et al. 2000 | 13 |

Verification:

- 30 original citation points before; 30 author-year citation points after.
- Expanding ranges and groups shows that all original numbers 1–24 remain represented.
- Zero bracketed numeric citations remain.
- Every target citation label is derived solely from its frozen reference-list entry.
- Reference count: **24 before / 24 after**.

## STROBE status and gaps

The checklist maps all 22 STROBE items and their cohort-specific subitems. Items not fully or explicitly addressed are marked in the PDF as follows:

- **1(a), reported:** the Abstract and `Methods — Study population, mortality linkage, and temporal split` describe mortality-linked NHANES 1999–2016 data with development and internal temporal-validation cohorts, identifying the observational temporal-validation design. STROBE permits design identification in the title or abstract.
- **6(b), not applicable:** no matched cohort design.
- **8, partial:** data sources and model-variable construction are given, but assay-level measurement detail is not reproduced in the manuscript.
- **10, reported:** no formal sample-size calculation was performed. The analytic sample was determined by mortality eligibility and complete availability of the required biomarkers, as documented in the Methods and Figure 1.
- **12(b), not applicable:** no subgroup analyses were performed. The reported time-interaction diagnostics are not subgroup analyses.
- **13(b), reported:** exclusions through mortality ineligibility and incomplete required biomarker data are mapped to Methods, Results, Figure 1, and Supplementary Tables S6–S7.
- **16(a), not applicable to separate unadjusted causal-effect estimates:** the study evaluates prediction and temporal validation rather than a causal effect. Predictive hazard ratios, discrimination estimates, and confidence intervals remain mapped to Results and Table 2.
- **16(b), not applicable to primary scores:** only calibration deciles are used.

No manuscript content was added to improve checklist completion.

## Validation record

- Revised manuscript rendered to 13 US-Letter pages and visually inspected page by page.
- Supplement rendered to 11 landscape pages and visually inspected page by page.
- STROBE checklist rendered to two landscape pages and visually inspected page by page.
- No clipping, overlap, missing glyphs, blank scientific pages, corrupted equations, or unreadable table boundaries were found.
- At the initial Biogerontology conversion, the target manuscript body had 178 XML body elements, matching the source.
- At the initial Biogerontology conversion, the only changed pre-reference elements were the 20 paragraphs containing citations.
- At the initial Biogerontology conversion, every equal-text pre-reference element was semantic-XML-identical.
- Both native Word tables are XML-identical.
- All seven displayed equation paragraphs are XML-identical.
- Embedded image bytes match the standalone `Fig1.png` and `Fig2.png` exactly.
- Embedded image drawing extents and figure-caption paragraphs are unchanged.
- Figure legends are unchanged.
- Every declaration except the explicitly approved Data and code availability paragraph is unchanged.
- At the initial Biogerontology conversion, the protected non-reference numeric-token sequence was identical: 307 tokens before and after.
- The only changed DOCX package parts at the Snapp stage are `word/document.xml` and the two embedded PNG media parts.
- Supplement source/target text is exactly identical after reversing the single permitted journal-name substitution.
- The Supplementary Material PDF and STROBE checklist PDF are byte-identical to their pre-Snapp files (SHA256 unchanged).
- Abstract, six keywords, both native Word tables, all seven displayed equations, all 24 references, all other declarations, both figure captions, and all other paragraphs are unchanged from the pre-Snapp Biogerontology manuscript.

## Remaining Biogerontology issues

1. **PRODUCTION-STAGE ISSUE:** seven equations are Cambria Math styled text rather than native OMML.
2. **ACCEPTABLE FOR INITIAL SUBMISSION:** frozen figure-caption punctuation differs from Springer house style.
3. **ACCEPTABLE FOR INITIAL SUBMISSION:** the submission system may relabel the supplementary file as an Online Resource/ESM item.

## Scientific-content freeze conclusion

**Confirmed: zero unapproved scientific prose changes.** Title, authorship, affiliation, contact details, approved abstract, approved keywords, Introduction, Methods, Results, Discussion, Limitations, Conclusions, all declarations other than the explicitly approved Data and code availability replacement, ethics wording, AI disclosure, tables, equations, numerical values, terminology, figure legends, references, and scientific figure content are unchanged.
