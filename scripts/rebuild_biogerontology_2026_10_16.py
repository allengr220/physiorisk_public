"""Mechanically assemble the versioned Biogerontology submission from frozen inputs."""

from __future__ import annotations

import copy
import csv
import io
from pathlib import Path
from zipfile import ZipFile

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from lxml import etree


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "submission" / "biogerontology"
VAL = ROOT / "outputs" / "physiorisk_v2_validation"
MANUSCRIPT = OUT / "PhysioRisk_Biogerontology_Manuscript_corrected_working_2026-10-16(1).docx"
SUPPLEMENT = ROOT / "manuscript" / "PhysioRisk_RS_Supplementary_Material.docx"
MANUSCRIPT_OUT = OUT / "PhysioRisk_Biogerontology_Manuscript_corrected_complete_2026-10-16.docx"
SUPPLEMENT_OUT = OUT / "PhysioRisk_Biogerontology_Supplementary_Material_corrected_2026-10-16.docx"

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}
qn = lambda local: f"{{{W}}}{local}"


def rows(name):
    with (VAL / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def patch_zip(source, destination, replacements):
    with ZipFile(source) as src, ZipFile(destination, "w") as dst:
        for member in src.infolist():
            dst.writestr(member, replacements.get(member.filename, src.read(member.filename)))


def paragraph(text, heading=False, size=18):
    p = etree.Element(qn("p"))
    ppr = etree.SubElement(p, qn("pPr"))
    if heading:
        style = etree.SubElement(ppr, qn("pStyle"))
        style.set(qn("val"), "Heading2")
        space = etree.SubElement(ppr, qn("spacing"))
        space.set(qn("before"), "180")
        space.set(qn("after"), "100")
    run = etree.SubElement(p, qn("r"))
    rpr = etree.SubElement(run, qn("rPr"))
    sz = etree.SubElement(rpr, qn("sz"))
    sz.set(qn("val"), str(size))
    node = etree.SubElement(run, qn("t"))
    node.text = text
    return p


def text_of(block):
    return "".join(block.xpath(".//w:t/text()", namespaces=NS))


def set_paragraph_text(block, value):
    ts = block.xpath(".//w:t", namespaces=NS)
    if not ts:
        block.append(paragraph(value))
        return
    ts[0].text = value
    for t in ts[1:]:
        t.text = ""


def table(headers, data, widths=None):
    count = len(headers)
    widths = widths or [9000 // count] * count
    tbl = etree.Element(qn("tbl"))
    pr = etree.SubElement(tbl, qn("tblPr"))
    tw = etree.SubElement(pr, qn("tblW"))
    tw.set(qn("w"), "9000")
    tw.set(qn("type"), "dxa")
    borders = etree.SubElement(pr, qn("tblBorders"))
    for side in ("top", "left", "bottom", "right", "insideH", "insideV"):
        b = etree.SubElement(borders, qn(side))
        b.set(qn("val"), "single")
        b.set(qn("sz"), "4")
        b.set(qn("color"), "B8B8B8")
    grid = etree.SubElement(tbl, qn("tblGrid"))
    for width in widths:
        g = etree.SubElement(grid, qn("gridCol"))
        g.set(qn("w"), str(width))
    for index, values in enumerate([headers] + data):
        tr = etree.SubElement(tbl, qn("tr"))
        if index == 0:
            trpr = etree.SubElement(tr, qn("trPr"))
            rep = etree.SubElement(trpr, qn("tblHeader"))
            rep.set(qn("val"), "true")
        for width, value in zip(widths, values):
            tc = etree.SubElement(tr, qn("tc"))
            tcpr = etree.SubElement(tc, qn("tcPr"))
            tcw = etree.SubElement(tcpr, qn("tcW"))
            tcw.set(qn("w"), str(width))
            tcw.set(qn("type"), "dxa")
            if index == 0:
                shade = etree.SubElement(tcpr, qn("shd"))
                shade.set(qn("fill"), "E8ECEF")
            p = etree.SubElement(tc, qn("p"))
            run = etree.SubElement(p, qn("r"))
            rpr = etree.SubElement(run, qn("rPr"))
            if index == 0:
                etree.SubElement(rpr, qn("b"))
            sz = etree.SubElement(rpr, qn("sz"))
            sz.set(qn("val"), "16")
            node = etree.SubElement(run, qn("t"))
            node.text = str(value)
    return tbl


def make_figure():
    data = rows("calibration_plot_data_v2.csv")
    assert len(data) == 20
    assert {(int(r["horizon_months"]), int(r["risk_decile"])) for r in data} == {
        (h, d) for h in (60, 96) for d in range(1, 11)
    }
    plt.rcParams.update({"font.size": 10, "font.family": "DejaVu Sans"})
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.35))
    for ax, horizon, title in zip(axes, (60, 96), ("5 years", "8 years")):
        part = sorted((r for r in data if int(r["horizon_months"]) == horizon), key=lambda x: int(x["risk_decile"]))
        x = [100 * float(r["mean_predicted_mortality"]) for r in part]
        y = [100 * float(r["KM_observed_mortality"]) for r in part]
        limit = 30 if horizon == 60 else 50
        ax.plot([0, limit], [0, limit], ls="--", color="#777777", lw=1.3)
        ax.plot(x, y, "o-", color="#176894", markersize=5, lw=1.4)
        ax.set(title=title, xlim=(0, limit), ylim=(0, limit), xlabel="Mean predicted mortality (%)")
        ax.grid(alpha=0.18)
        ax.set_aspect("equal", adjustable="box")
    axes[0].set_ylabel("Kaplan–Meier observed mortality (%)")
    fig.tight_layout(pad=2.0)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=220, facecolor="white")
    plt.close(fig)
    return buf.getvalue()


def build_manuscript():
    figure = make_figure()
    patch_zip(MANUSCRIPT, MANUSCRIPT_OUT, {"word/media/image3.png": figure})


def build_supplement():
    with ZipFile(SUPPLEMENT) as src:
        root = etree.fromstring(src.read("word/document.xml"))
    body = root.find(qn("body"))
    blocks = list(body)
    heading = lambda number: next(b for b in body if text_of(b).startswith(f"Supplementary Table S{number}."))
    replace_table = lambda number, new: body.replace(heading(number).getnext(), new)

    # The existing supplement has no supplementary methods section.
    methods = [
        paragraph("Supplementary Methods", heading=True),
        paragraph("Laboratory measurements were harmonized across NHANES cycles to prespecified units before residualization or score construction. PhysioRisk used creatinine in mg/dL. For PhenoAge NCP, albumin was expressed in g/L, creatinine in µmol/L, and glucose in mmol/L before application of the published coefficients."),
        paragraph("PhenoAge NCP was calculated as:"),
        paragraph("−19.907 − 0.0336 × albumin (g/L) + 0.0095 × creatinine (µmol/L) + 0.1953 × glucose (mmol/L) − 0.0120 × lymphocyte percentage + 0.0268 × mean corpuscular volume (fL) + 0.3306 × red cell distribution width (%) + 0.00188 × alkaline phosphatase (U/L) + 0.0554 × white blood cell count (10³/µL) + 0.0804 × age (years)."),
        paragraph("C-reactive protein was omitted. Albumin was converted from g/dL to g/L, creatinine from mg/dL to µmol/L, and glucose was harmonized across survey cycles to mmol/L before applying the coefficients. Glucose entered the predictor linearly."),
        paragraph("Glucose was harmonized to mmol/L before calculation of PhenoAge NCP. For 2001–2002 and 2003–2004, the NHANES SI variable LBDSGLSI was used directly in mmol/L. For 1999–2000 and 2005–2016, LBXGLU was supplied in mg/dL and converted to mmol/L by multiplication by 0.05551."),
    ]
    insert_at = list(body).index(heading(1))
    for offset, p in enumerate(methods):
        body.insert(insert_at + offset, p)

    boot = rows("paired_cindex_bootstrap_v2.csv")
    labels = ["CalibratedTotalRisk − DemoRisk", "CalibratedTotalRisk − PhenoAge NCP", "PhysioRisk − PhenoAge NCP acceleration"]
    s1 = [[label, f'{float(r["observed_delta_C_A_minus_B"]):.5f}'.replace("-", "−"),
           f'{float(r["percentile_95CI_low"]):.5f}–{float(r["percentile_95CI_high"]):.5f}'.replace("-", "−"),
           f'{float(r["proportion_bootstrap_delta_above_zero"]):.4f}']
          for label, r in zip(labels, boot)]
    replace_table(1, table(["Contrast", "ΔC (A − B)", "95% CI", "Bootstrap proportion ΔC > 0"], s1,
                           [3100, 1400, 2300, 2200]))
    set_paragraph_text(heading(1).getnext().getnext(), "Note: Paired percentile intervals were obtained from 2,000 participant bootstrap replicates in the temporal-validation cohort (seed 20260821). Contrast estimates and interval limits are shown to five decimal places.")

    mapping = {"DemoRisk": "DemoRisk", "PhysioRisk_2axis_v2": "PhysioRisk", "CalibratedTotalRisk_v2": "CalibratedTotalRisk", "PhenoAge_NCP_v2": "PhenoAge NCP", "PhenoAge_NCP_acceleration_v2": "PhenoAge NCP acceleration"}
    ph = rows("ph_diagnostics_v2.csv")
    s2 = [[mapping[r["model"]], f'{float(r["test_statistic"]):.3f}',
           "0.000670" if r["model"] == "CalibratedTotalRisk_v2" else f'{float(r["p_value"]):.4f}',
           "Yes" if r["descriptive_flag_p_lt_0_01"] == "True" else "No",
           r["scaled_residual_band_summary"].replace("-", "−")]
          for r in ph]
    replace_table(2, table(["Score", "Statistic", "P value", "Flag at p<0.01", "Scaled-residual region summary"], s2,
                           [2200, 900, 900, 1100, 3900]))
    set_paragraph_text(heading(2).getnext().getnext(), "Note: Schoenfeld diagnostics used the rank time transform in 6,739 temporal-validation participants with 416 deaths. The prespecified descriptive flag was p<0.01 without multiplicity adjustment.")

    ti = rows("time_interactions_v2.csv")
    assert len(ti) == 1
    r = ti[0]
    replace_table(3, table(["Score", "Log-time interaction coefficient", "95% CI", "P value", "Flag at p<0.01"],
                           [["CalibratedTotalRisk", f'{float(r["time_interaction_coefficient"]):.5f}',
                             f'{float(r["time_interaction_95CI_low"]):.5f}–{float(r["time_interaction_95CI_high"]):.5f}',
                             f'{float(r["time_interaction_p_value"]):.5f}', "No"]],
                           [2200, 2400, 1700, 1200, 1500]))
    set_paragraph_text(heading(3).getnext().getnext(), "Note: The diagnostic interaction was score × log(time in months / 60), using the temporal-validation cohort standard deviation. It did not replace or refit the fixed predictor used in temporal validation.")

    cal = rows("fixed_horizon_calibration_v2.csv")
    assert [r["horizon_months"] for r in cal] == ["60", "96"]
    fields = [
        ("IPCW usable N", "IPCW_usable_N", lambda x: f"{int(x):,}"),
        ("Training baseline survival", "development_baseline_survival", lambda x: f"{float(x):.6f}"),
        ("Mean predicted mortality", "mean_predicted_mortality", lambda x: f"{float(x):.5f}"),
        ("KM observed mortality", "KM_observed_mortality", lambda x: f"{float(x):.5f}"),
        ("Observed − predicted", "observed_minus_predicted", lambda x: f"{float(x):.5f}".replace("-", "−")),
        ("O/E ratio", "observed_to_expected_ratio", lambda x: f"{float(x):.3f}"),
        ("IPCW logistic intercept", "IPCW_logistic_calibration_intercept", lambda x: f"{float(x):.3f}".replace("-", "−")),
        ("IPCW logistic slope", "IPCW_logistic_calibration_slope", lambda x: f"{float(x):.3f}"),
        ("IPCW Brier score", "IPCW_Brier_score", lambda x: f"{float(x):.4f}"),
    ]
    replace_table(4, table(["Metric", "5 years", "8 years"], [[label, fmt(cal[0][key]), fmt(cal[1][key])] for label, key, fmt in fields], [4500, 2250, 2250]))
    set_paragraph_text(heading(4).getnext().getnext(), "Note: Absolute risks used development-derived coefficients and baseline survival. Horizon-specific logistic calibration and Brier scores used temporal-validation censoring weights for evaluation; known outcomes contributed directly. No temporal recalibration occurred. Global Cox calibration slope: 0.804 (95% CI 0.755–0.852). No bootstrap confidence intervals were estimated for horizon-specific slopes.")

    disc = rows("censoring_robust_discrimination_v2.csv")
    by_model = {}
    for r in disc:
        by_model.setdefault(r["model"], {})[int(r["horizon_months"])] = r
    s5 = []
    for key in mapping:
        five, eight = by_model[key][60], by_model[key][96]
        s5.append([mapping[key], f'{float(five["Uno_C_IPCW_truncated_at_horizon"]):.3f}',
                   f'{float(eight["Uno_C_IPCW_truncated_at_horizon"]):.3f}',
                   f'{float(five["cumulative_dynamic_AUC_IPCW"]):.3f}',
                   f'{float(eight["cumulative_dynamic_AUC_IPCW"]):.3f}'])
    replace_table(5, table(["Score", "Uno C, 5 years", "Uno C, 8 years", "AUC, 5 years", "AUC, 8 years"], s5,
                           [3000, 1500, 1500, 1500, 1500]))

    primary = {r["model"]: r for r in rows("primary_validation_metrics_v2.csv")}
    s8 = []
    for analysis in ("common complete case", "training-derived imputation"):
        for key in ("PhysioRisk_2axis_v2", "PhenoAge_NCP_v2"):
            r = primary[key]
            s8.append([analysis, mapping[key], "6,739", "416", f'{float(r["Harrell_C"]):.3f}', f'{float(r["pearson_age_correlation"]):.3f}'])
    replace_table(8, table(["Analysis", "Score", "N", "Deaths", "C-index", "Age correlation"], s8,
                           [2400, 2500, 900, 900, 1100, 1200]))
    set_paragraph_text(heading(8).getnext().getnext(), "Note: All 6,739 temporal-validation participants had the biomarkers required for both scores. Training-derived imputation changed no observations. Extension to excluded participants was not attempted because doing so would require a separately specified missing-data strategy and would change the retained complete-case validation design.")

    # Source-artifact references attached to changed tables point to superseded files.
    for number in (1, 2, 3, 4, 5, 8):
        provenance = heading(number).getnext().getnext().getnext()
        assert text_of(provenance).startswith("Provenance:")
        body.remove(provenance)
    h9 = heading(9)
    s9_blocks = [h9, h9.getnext(), h9.getnext().getnext(), h9.getnext().getnext().getnext()]
    for block in s9_blocks:
        body.remove(block)

    xml = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)
    patch_zip(SUPPLEMENT, SUPPLEMENT_OUT, {"word/document.xml": xml})


if __name__ == "__main__":
    build_manuscript()
    build_supplement()
    print(MANUSCRIPT_OUT)
    print(SUPPLEMENT_OUT)
