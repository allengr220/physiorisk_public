#!/usr/bin/env python3
"""Build Sprint 4 manuscript-facing tables and the calibration figure.

All displayed estimates are read from frozen generated CSV artifacts.
"""

from pathlib import Path
import csv
import hashlib
import json
import os

import pandas as pd
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "tables"
OUT = ROOT / "manuscript" / "generated"
DATA_DIR = Path(os.environ.get("PHYSIORISK_DATA_DIR", "/home/ubuntu2204/longevity/data/physiorisk/data"))
SCORED_FILES = {
    "development": (
        "physiorisk_2axis_v1_train_scored_from_frozen_baseline_levinenocrp.parquet",
        "e8f435b5a8b68dbb477f04bad280252f563b9323e9bc9dea4eb7e945c22cbb86",
    ),
    "temporal_validation": (
        "physiorisk_2axis_v1_test_scored_from_frozen_baseline_levinenocrp.parquet",
        "1455e24e8ca3e1f68eb58a779f7a4d48e46b8e54fa435ec00de5cf51256d08ca",
    ),
}


def read_csv(name):
    with (TABLES / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(name, fieldnames, rows):
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / name).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def fmt_ci(value, low, high, digits=3):
    return f"{float(value):.{digits}f} ({float(low):.{digits}f}–{float(high):.{digits}f})"


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def table1():
    frames, inputs = {}, {}
    for cohort, (filename, expected_hash) in SCORED_FILES.items():
        path = DATA_DIR / filename
        actual_hash = sha256(path)
        if actual_hash != expected_hash:
            raise RuntimeError(f"SHA256 mismatch for {path}: {actual_hash} != {expected_hash}")
        frames[cohort] = pd.read_parquet(path)
        inputs[cohort] = {"path": str(path), "sha256": actual_hash, "rows": len(frames[cohort])}

    development = frames["development"]
    temporal = frames["temporal_validation"]
    if (len(development), len(temporal)) != (13090, 6739):
        raise RuntimeError("Unexpected scored-parquet cohort sizes")

    def describe(frame):
        n = len(frame)
        female = int(frame["RIAGENDR"].eq(2).sum())
        deaths = int(frame["MORTSTAT"].sum())
        followup = frame["PERMTH_INT"]
        return {
            "Participants": f"{n:,}",
            "Age, mean (SD), years": f"{frame['RIDAGEYR'].mean():.1f} ({frame['RIDAGEYR'].std(ddof=1):.1f})",
            "Female, n (%)": f"{female:,} ({100 * female / n:.1f}%)",
            "Deaths, n (%)": f"{deaths:,} ({100 * deaths / n:.1f}%)",
            "Follow-up, median (IQR), months": (
                f"{followup.median():.0f} ({followup.quantile(.25):.0f}–{followup.quantile(.75):.0f})"
            ),
        }

    dev, val = describe(development), describe(temporal)
    rows = [
        {"Characteristic": characteristic, "Development (1999–2010)": dev[characteristic],
         "Temporal validation (2011–2016)": val[characteristic]}
        for characteristic in dev
    ]
    write_csv("table1_revised.csv", list(rows[0]), rows)
    metadata = {
        "description": "Descriptive Table 1 regenerated without model fitting from SHA256-locked scored parquets.",
        "inputs": inputs,
        "female_code": "RIAGENDR == 2",
        "followup_units": "months",
        "standard_deviation_ddof": 1,
        "quantile_method": "pandas default linear interpolation",
    }
    (OUT / "table1_revised.metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )


def cohort_flow_figure():
    svg = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="900" height="560" viewBox="0 0 900 560">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#222}.box{fill:#f5f8fb;stroke:#2369a1;stroke-width:2}.arrow{stroke:#555;stroke-width:2;fill:none}</style>',
        '<defs><marker id="a" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto"><path d="M0,0 L0,6 L8,3 z" fill="#555"/></marker></defs>',
    ]
    boxes = [
        (250, 25, 400, 70, "NHANES 1999–2016 source cycles", "n=92,062"),
        (250, 145, 400, 70, "Mortality eligible", "n=53,255"),
        (250, 265, 400, 70, "Biomarker-complete analytic cohort", "n=19,829"),
        (45, 445, 360, 70, "Development (1999–2010)", "n=13,090"),
        (495, 445, 360, 70, "Temporal validation (2011–2016)", "n=6,739"),
    ]
    for x, y, w, h, title, count in boxes:
        svg.extend([
            f'<rect class="box" x="{x}" y="{y}" width="{w}" height="{h}" rx="8"/>',
            f'<text x="{x+w/2}" y="{y+29}" text-anchor="middle" font-size="18">{title}</text>',
            f'<text x="{x+w/2}" y="{y+54}" text-anchor="middle" font-size="17">{count}</text>',
        ])
    svg.extend([
        '<line class="arrow" x1="450" y1="95" x2="450" y2="140" marker-end="url(#a)"/>',
        '<line class="arrow" x1="450" y1="215" x2="450" y2="260" marker-end="url(#a)"/>',
        '<path class="arrow" d="M450 335 L450 385 L225 385 L225 440" marker-end="url(#a)"/>',
        '<path class="arrow" d="M450 335 L450 385 L675 385 L675 440" marker-end="url(#a)"/>',
        '</svg>',
    ])
    (OUT / "figure1_cohort_flow.svg").write_text("\n".join(svg), encoding="utf-8")
    image = Image.new("RGB", (1800, 1120), "white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("DejaVuSans.ttf", 34)
    boxes_2x = [(2*x, 2*y, 2*w, 2*h, title, count) for x, y, w, h, title, count in boxes]
    for x, y, w, h, title, count in boxes_2x:
        draw.rounded_rectangle((x, y, x+w, y+h), radius=16, fill="#f5f8fb", outline="#2369a1", width=4)
        draw.text((x+w/2, y+52), title, font=font, fill="#222", anchor="mm")
        draw.text((x+w/2, y+104), count, font=font, fill="#222", anchor="mm")
    arrow = {"fill": "#555", "width": 4}
    draw.line((900, 190, 900, 280), **arrow); draw.polygon(((890,270),(910,270),(900,288)), fill="#555")
    draw.line((900, 430, 900, 520), **arrow); draw.polygon(((890,510),(910,510),(900,528)), fill="#555")
    draw.line((900, 670, 900, 770, 450, 770, 450, 880), **arrow); draw.polygon(((440,870),(460,870),(450,888)), fill="#555")
    draw.line((900, 670, 900, 770, 1350, 770, 1350, 880), **arrow); draw.polygon(((1340,870),(1360,870),(1350,888)), fill="#555")
    image.save(OUT / "figure1_cohort_flow.png", dpi=(200, 200))


def table2():
    validation = {r["model"]: r for r in read_csv("validation_v2.csv")}
    order = [
        ("DemoRisk", "DemoRisk"),
        ("PhysioRisk", "PhysioRisk_convergence_corrected"),
        ("CalibratedTotalRisk", "CalibratedTotalRisk"),
        ("PhenoAge NCP", "PhenoAge NCP"),
        ("PhenoAge NCP acceleration", "PhenoAge NCP acceleration"),
    ]
    rows = []
    for label, key in order:
        r = validation[key]
        rows.append({
            "Model": label,
            "C-index (95% CI)": fmt_ci(r["C_index"], r["C_index_bootstrap_95CI_low"], r["C_index_bootstrap_95CI_high"]),
            "HR per validation SD (95% CI)": fmt_ci(r["HR_per_actual_1SD"], r["HR_95CI_low"], r["HR_95CI_high"]),
            "Age correlation": f"{float(r['age_correlation']):.3f}",
        })
    write_csv("table2_revised.csv", list(rows[0]), rows)


def supplementary_tables():
    mappings = {
        "table_s1_paired_cindex_contrasts.csv": "cindex_bootstrap_contrasts.csv",
        "table_s2_ph_diagnostics.csv": "ph_diagnostics.csv",
        "table_s3_time_interactions.csv": "ph_time_interaction.csv",
        "table_s4_calibration.csv": "calibration_fixed_horizons.csv",
        "table_s5_censoring_robust_discrimination.csv": "censoring_robust_discrimination.csv",
        "table_s6_missingness_by_cycle.csv": "missingness_by_cycle.csv",
        "table_s7_included_excluded.csv": "cohort_included_excluded_characteristics.csv",
        "table_s8_comparator_sensitivity.csv": "comparator_sensitivity.csv",
    }
    OUT.mkdir(parents=True, exist_ok=True)
    for target, source in mappings.items():
        (OUT / target).write_bytes((TABLES / source).read_bytes())
    historical = read_csv("physiorisk_vs_phenoage_aligned_comparison.csv")
    labeled = []
    for row in historical:
        labeled.append({
            "status": "historical_submitted_not_current",
            "interpretation": "provenance_only; PhysioRisk HR did not converge and TotalRisk_2axis is the obsolete unit-weight composite",
            **row,
        })
    write_csv("table_s9_historical_submitted_results.csv", list(labeled[0]), labeled)


def calibration_figure():
    rows = read_csv("calibration_plot_data.csv")
    width, height = 960, 430
    panels = [(70, 75, 380, 300, "60", "5 years"), (550, 75, 380, 300, "96", "8 years")]
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#222}.axis{stroke:#222;stroke-width:1}.grid{stroke:#ddd;stroke-width:1}.ideal{stroke:#777;stroke-dasharray:5 5}.data{stroke:#2369a1;stroke-width:2;fill:none}.point{fill:#2369a1}</style>',
        '<text x="480" y="28" text-anchor="middle" font-size="18">CalibratedTotalRisk fixed-horizon calibration</text>',
    ]
    max_risk = 0.5
    for left, top, pw, ph, horizon, title in panels:
        subset = [r for r in rows if r["horizon_months"] == horizon]
        x = [float(r["mean_predicted_risk"]) for r in subset]
        y = [float(r["KM_observed_risk"]) for r in subset]
        sx = lambda value: left + value / max_risk * pw
        sy = lambda value: top + ph - value / max_risk * ph
        for tick in (0, 0.1, 0.2, 0.3, 0.4, 0.5):
            xx, yy = sx(tick), sy(tick)
            svg.extend([
                f'<line class="grid" x1="{xx:.1f}" y1="{top}" x2="{xx:.1f}" y2="{top+ph}"/>',
                f'<line class="grid" x1="{left}" y1="{yy:.1f}" x2="{left+pw}" y2="{yy:.1f}"/>',
                f'<text x="{xx:.1f}" y="{top+ph+20}" text-anchor="middle" font-size="11">{tick:.1f}</text>',
                f'<text x="{left-10}" y="{yy+4:.1f}" text-anchor="end" font-size="11">{tick:.1f}</text>',
            ])
        svg.extend([
            f'<line class="axis" x1="{left}" y1="{top+ph}" x2="{left+pw}" y2="{top+ph}"/>',
            f'<line class="axis" x1="{left}" y1="{top}" x2="{left}" y2="{top+ph}"/>',
            f'<line class="ideal" x1="{left}" y1="{top+ph}" x2="{left+pw}" y2="{top}"/>',
            f'<text x="{left+pw/2}" y="{top-14}" text-anchor="middle" font-size="15">{title}</text>',
            f'<text x="{left+pw/2}" y="{top+ph+43}" text-anchor="middle" font-size="12">Mean predicted mortality</text>',
        ])
        points = " ".join(f"{sx(a):.1f},{sy(b):.1f}" for a, b in zip(x, y))
        svg.append(f'<polyline class="data" points="{points}"/>')
        for a, b in zip(x, y):
            svg.append(f'<circle class="point" cx="{sx(a):.1f}" cy="{sy(b):.1f}" r="3.5"/>')
    svg.extend([
        '<text x="18" y="225" text-anchor="middle" font-size="12" transform="rotate(-90 18 225)">Kaplan–Meier observed mortality</text>',
        '</svg>',
    ])
    (OUT / "figure_calibration_5y_8y.svg").write_text("\n".join(svg), encoding="utf-8")
    scale = 2
    image = Image.new("RGB", (width * scale, height * scale), "white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("DejaVuSans.ttf", 23)
    title_font = ImageFont.truetype("DejaVuSans.ttf", 32)
    draw.text((width, 42), "CalibratedTotalRisk fixed-horizon calibration", font=title_font, fill="#222", anchor="mm")
    for left, top, pw, ph, horizon, title in panels:
        subset = [r for r in rows if r["horizon_months"] == horizon]
        sx = lambda value: scale * (left + value / max_risk * pw)
        sy = lambda value: scale * (top + ph - value / max_risk * ph)
        for tick in (0, .1, .2, .3, .4, .5):
            xx, yy = sx(tick), sy(tick)
            draw.line((xx, top*scale, xx, (top+ph)*scale), fill="#dddddd", width=2)
            draw.line((left*scale, yy, (left+pw)*scale, yy), fill="#dddddd", width=2)
            draw.text((xx, (top+ph)*scale+25), f"{tick:.1f}", font=font, fill="#222", anchor="mt")
            draw.text((left*scale-16, yy), f"{tick:.1f}", font=font, fill="#222", anchor="rm")
        draw.line((left*scale, (top+ph)*scale, (left+pw)*scale, top*scale), fill="#777777", width=2)
        draw.rectangle((left*scale, top*scale, (left+pw)*scale, (top+ph)*scale), outline="#222", width=2)
        draw.text(((left+pw/2)*scale, (top-15)*scale), title, font=font, fill="#222", anchor="ms")
        points = [(sx(float(r["mean_predicted_risk"])), sy(float(r["KM_observed_risk"]))) for r in subset]
        draw.line(points, fill="#2369a1", width=4)
        for x, y in points: draw.ellipse((x-7, y-7, x+7, y+7), fill="#2369a1")
    image.save(OUT / "figure_calibration_5y_8y.png", dpi=(200, 200))


if __name__ == "__main__":
    table1()
    table2()
    supplementary_tables()
    cohort_flow_figure()
    calibration_figure()
