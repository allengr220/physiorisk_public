"""Restore historical supplement structure around approved frozen numerical changes."""

from __future__ import annotations

import copy
import csv
from pathlib import Path
from zipfile import ZipFile

from lxml import etree


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "manuscript/PhysioRisk_RS_Supplementary_Material.docx"
CURRENT = ROOT / "submission/biogerontology/PhysioRisk_Biogerontology_Supplementary_Material_corrected_2026-10-16.docx"
OUTPUT = ROOT / "submission/biogerontology/PhysioRisk_Biogerontology_Supplementary_Material_corrected_preserved_2026-10-16.docx"
VAL = ROOT / "outputs/physiorisk_v2_validation"
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
N = {"w": W}
q = lambda local: f"{{{W}}}{local}"


def rows(name):
    with (VAL / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def content(block):
    return "".join(block.xpath(".//w:t/text()", namespaces=N))


def replace_text(block, value):
    ts = block.xpath(".//w:t", namespaces=N)
    assert ts
    ts[0].text = str(value)
    for t in ts[1:]:
        t.text = ""


def cells(table):
    return [[c for c in tr.findall(q("tc"))] for tr in table.findall(q("tr"))]


def fill_table(table, data):
    old = cells(table)
    assert len(old) == len(data)
    for outrow, values in zip(old, data):
        assert len(outrow) == len(values)
        for cell, value in zip(outrow, values):
            replace_text(cell, value)


def source_section(body, number):
    heading = next(b for b in body if content(b).startswith(f"Supplementary Table S{number}."))
    return [heading, heading.getnext(), heading.getnext().getnext(), heading.getnext().getnext().getnext()]


def current_section(body, number):
    heading = next(b for b in body if content(b).startswith(f"Supplementary Table S{number}."))
    return [heading, heading.getnext(), heading.getnext().getnext()]


def install(body, source_body, number, table, note=None, provenance=None):
    original = source_section(source_body, number)
    current = current_section(body, number)
    body.replace(current[1], table)
    body.replace(current[2], copy.deepcopy(original[2]) if note is None else note)
    path = copy.deepcopy(original[3])
    replace_text(path, f"Provenance: outputs/physiorisk_v2_validation/{provenance}.")
    body.insert(body.index(current[0]) + 3, path)


def main():
    with ZipFile(SOURCE) as z:
        source_root = etree.fromstring(z.read("word/document.xml"))
    with ZipFile(CURRENT) as z:
        root = etree.fromstring(z.read("word/document.xml"))
    source_body = source_root.find(q("body"))
    body = root.find(q("body"))

    # The submitted PDF contains this title metadata; the editable source omitted it.
    author = next(b for b in body if content(b) == "Gregory S. Allen")
    title_meta = [
        ("Biogerontology", True),
        ("Independent researcher, Cuenca, Ecuador", False),
        ("Corresponding author: Gregory S. Allen", False),
        ("Email: allengr220@gmail.com", False),
    ]
    journal = copy.deepcopy(author)
    replace_text(journal, title_meta[0][0])
    ppr = journal.find(q("pPr"))
    if ppr is None:
        ppr = etree.Element(q("pPr"))
        journal.insert(0, ppr)
    spacing = ppr.find(q("spacing"))
    if spacing is None:
        spacing = etree.SubElement(ppr, q("spacing"))
    spacing.set(q("before"), "600")
    spacing.set(q("after"), "260")
    body.insert(body.index(author), journal)
    for offset, (label, _) in enumerate(title_meta[1:], start=1):
        p = copy.deepcopy(author)
        replace_text(p, label)
        body.insert(body.index(author) + offset, p)

    boot = rows("paired_cindex_bootstrap_v2.csv")
    labels = ["CalibratedTotalRisk − DemoRisk", "CalibratedTotalRisk − PhenoAge NCP", "PhysioRisk − PhenoAge NCP acceleration"]
    s1 = copy.deepcopy(source_section(source_body, 1)[1])
    s1_data = [[content(c) for c in cells(s1)[0]]]
    for label, r in zip(labels, boot):
        s1_data.append([label, "temporal_test", f'{float(r["observed_delta_C_A_minus_B"]):.5f}'.replace("-", "−"),
                        f'{float(r["percentile_95CI_low"]):.5f}'.replace("-", "−"),
                        f'{float(r["percentile_95CI_high"]):.5f}'.replace("-", "−"),
                        f'{float(r["proportion_bootstrap_delta_above_zero"]):.4f}', "2000", "20260821"])
    fill_table(s1, s1_data)
    install(body, source_body, 1, s1, provenance="paired_cindex_bootstrap_v2.csv")

    labels_by_model = {"DemoRisk": "DemoRisk", "PhysioRisk_2axis_v2": "PhysioRisk", "CalibratedTotalRisk_v2": "CalibratedTotalRisk", "PhenoAge_NCP_v2": "PhenoAge NCP", "PhenoAge_NCP_acceleration_v2": "PhenoAge NCP acceleration"}
    s2 = copy.deepcopy(source_section(source_body, 2)[1])
    original_rows = s2.findall(q("tr"))
    # Replace the two historical axis rows with the two corrected comparator rows.
    for tr in original_rows[4:]:
        s2.remove(tr)
    for _ in range(2):
        s2.append(copy.deepcopy(original_rows[1]))
    s2_data = [[content(c) for c in cells(s2)[0]]]
    for r in rows("ph_diagnostics_v2.csv"):
        s2_data.append([labels_by_model[r["model"]], "temporal_test", "6,739", "416", "rank",
                        f'{float(r["test_statistic"]):.3f}', f'{float(r["p_value"]):.8f}',
                        r["descriptive_flag_p_lt_0_01"],
                        "p<0.01 (prespecified descriptive flag; no multiplicity adjustment)",
                        r["cox_convergence_warning"], r["scaled_residual_band_summary"]])
    fill_table(s2, s2_data)
    install(body, source_body, 2, s2, provenance="ph_diagnostics_v2.csv")

    ti = rows("time_interactions_v2.csv")
    assert len(ti) == 1 and ti[0]["model"] == "CalibratedTotalRisk_v2"
    r = ti[0]
    s3 = copy.deepcopy(source_section(source_body, 3)[1])
    for tr in s3.findall(q("tr"))[1:3]:
        s3.remove(tr)
    # The e-fold multiplier has no frozen field. All three horizon HR fields do.
    grid = s3.find(q("tblGrid"))
    grid.remove(grid.findall(q("gridCol"))[11])
    for tr in s3.findall(q("tr")):
        tr.remove(tr.findall(q("tc"))[11])
    s3_data = [[content(c) for c in cells(s3)[0]], [
        "CalibratedTotalRisk", "6,739", "416", "actual temporal-cohort SD",
        "score_z * log(time_months/60)", "60", f'{float(r["main_log_HR_at_60m"]):.3f}',
        f'{float(r["HR_per_SD_at_12m"]):.3f}', f'{float(r["HR_per_SD_at_60m"]):.3f}',
        f'{float(r["HR_per_SD_at_96m"]):.3f}', f'{float(r["time_interaction_coefficient"]):.5f}',
        f'{float(r["time_interaction_95CI_low"]):.5f}', f'{float(r["time_interaction_95CI_high"]):.5f}',
        f'{float(r["time_interaction_p_value"]):.5f}', r["direction"]]]
    fill_table(s3, s3_data)
    s3_note = copy.deepcopy(source_section(source_body, 3)[2])
    replace_text(s3_note, content(s3_note) + " The interaction did not meet the prespecified p<0.01 descriptive flag (No).")
    install(body, source_body, 3, s3, note=s3_note, provenance="time_interactions_v2.csv")

    s4 = copy.deepcopy(source_section(source_body, 4)[1])
    s4_data = [[content(c) for c in cells(s4)[0]]]
    for r in rows("fixed_horizon_calibration_v2.csv"):
        s4_data.append([r["horizon_months"], f'{float(r["development_baseline_survival"]):.6f}',
                        f'{float(r["mean_predicted_mortality"]):.5f}', f'{float(r["KM_observed_mortality"]):.5f}',
                        f'{float(r["observed_minus_predicted"]):.5f}'.replace("-", "−"),
                        f'{float(r["observed_to_expected_ratio"]):.3f}',
                        f'{float(r["global_Cox_calibration_slope"]):.3f}',
                        f'{float(r["global_Cox_calibration_slope_95CI_low"]):.3f}',
                        f'{float(r["global_Cox_calibration_slope_95CI_high"]):.3f}',
                        f'{float(r["IPCW_logistic_calibration_intercept"]):.3f}'.replace("-", "−"),
                        f'{float(r["IPCW_logistic_calibration_slope"]):.3f}',
                        f'{float(r["IPCW_Brier_score"]):.4f}', f'{int(r["IPCW_usable_N"]):,}', "True"])
    fill_table(s4, s4_data)
    install(body, source_body, 4, s4, provenance="fixed_horizon_calibration_v2.csv")

    s5 = current_section(body, 5)
    p5 = copy.deepcopy(source_section(source_body, 5)[3])
    replace_text(p5, "Provenance: outputs/physiorisk_v2_validation/censoring_robust_discrimination_v2.csv.")
    body.insert(body.index(s5[0]) + 3, p5)

    primary = {r["model"]: r for r in rows("primary_validation_metrics_v2.csv")}
    s8 = copy.deepcopy(source_section(source_body, 8)[1])
    for row in cells(s8)[1:]:
        model = "PhysioRisk_2axis_v2" if content(row[1]) == "PhysioRisk" else "PhenoAge_NCP_v2"
        r = primary[model]
        replace_text(row[5], f'{float(r["Harrell_C"]):.3f}')
        replace_text(row[6], f'{float(r["pearson_age_correlation"]):.3f}')
        if content(row[0]) == "common_training_derived_imputation":
            replace_text(row[7], "no-op in retained benchmark because all required biomarkers are observed")
            replace_text(row[8], "performed as degenerate no-missing sensitivity; extension to excluded participants not attempted")
    s8_note = copy.deepcopy(source_section(source_body, 8)[2])
    replace_text(s8_note, "Note: All 6,739 temporal-validation participants in the retained benchmark already had the biomarkers required for both scores. Common training-derived imputation was therefore a no-op and changed no observations. Extension to excluded participants was not attempted because doing so would require a separately specified missing-data strategy and would change the retained complete-case validation design.")
    install(body, source_body, 8, s8, note=s8_note, provenance="primary_validation_metrics_v2.csv")

    xml = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)
    with ZipFile(CURRENT) as src, ZipFile(OUTPUT, "w") as dst:
        for member in src.infolist():
            dst.writestr(member, xml if member.filename == "word/document.xml" else src.read(member.filename))
    print(OUTPUT)


if __name__ == "__main__":
    main()
