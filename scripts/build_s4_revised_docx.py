#!/usr/bin/env python3
"""Render the publication-facing Markdown as a clean Word review copy."""

from copy import deepcopy
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from xml.etree import ElementTree as ET
import csv
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "manuscript" / "archive" / "PhysioRisk_BMC_MIDM_v2.docx"
MARKDOWN = ROOT / "manuscript" / "archive" / "PhysioRisk_BMC_MIDM_v3_revised.md"
TARGET = ROOT / "manuscript" / "archive" / "PhysioRisk_BMC_MIDM_v3_revised.docx"
GENERATED = ROOT / "manuscript" / "generated"
WINDOWS_PYTHON = Path("/mnt/c/Python313/python.exe")
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
PIC = "http://schemas.openxmlformats.org/drawingml/2006/picture"
REL = "http://schemas.openxmlformats.org/package/2006/relationships"
for prefix, uri in (("w", W), ("r", R), ("wp", WP), ("a", A), ("pic", PIC)):
    ET.register_namespace(prefix, uri)


def q(ns, tag):
    return f"{{{ns}}}{tag}"


def clean(text):
    return re.sub(r"\*\*(.*?)\*\*", r"\1", text).replace("`", "")


def paragraph(text="", style=None, bold=False, keep_next=False, page_break=False):
    p = ET.Element(q(W, "p"))
    if style or keep_next or page_break:
        ppr = ET.SubElement(p, q(W, "pPr"))
        if style:
            ET.SubElement(ppr, q(W, "pStyle")).set(q(W, "val"), style)
        if keep_next:
            ET.SubElement(ppr, q(W, "keepNext"))
        if page_break:
            ET.SubElement(ppr, q(W, "pageBreakBefore"))
    run = ET.SubElement(p, q(W, "r"))
    if bold:
        ET.SubElement(ET.SubElement(run, q(W, "rPr")), q(W, "b"))
    node = ET.SubElement(run, q(W, "t"))
    node.text = clean(text)
    return p


def table_from_csv(path, widths, nowrap_columns=()):
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.reader(handle))
    tbl = ET.Element(q(W, "tbl"))
    pr = ET.SubElement(tbl, q(W, "tblPr"))
    ET.SubElement(pr, q(W, "tblStyle")).set(q(W, "val"), "TableGrid")
    ET.SubElement(pr, q(W, "tblW"), {q(W, "w"): str(sum(widths)), q(W, "type"): "dxa"})
    ET.SubElement(pr, q(W, "tblLayout")).set(q(W, "type"), "fixed")
    grid = ET.SubElement(tbl, q(W, "tblGrid"))
    for width in widths:
        ET.SubElement(grid, q(W, "gridCol")).set(q(W, "w"), str(width))
    for row_i, row in enumerate(rows):
        tr = ET.SubElement(tbl, q(W, "tr"))
        if row_i == 0:
            ET.SubElement(ET.SubElement(tr, q(W, "trPr")), q(W, "tblHeader"))
        for col_i, value in enumerate(row):
            tc = ET.SubElement(tr, q(W, "tc"))
            tcpr = ET.SubElement(tc, q(W, "tcPr"))
            ET.SubElement(tcpr, q(W, "tcW"), {q(W, "w"): str(widths[col_i]), q(W, "type"): "dxa"})
            if col_i in nowrap_columns:
                ET.SubElement(tcpr, q(W, "noWrap"))
            tc.append(paragraph(value, bold=(row_i == 0)))
    return tbl


def image_paragraph(rel_id, name, cx=5943600, cy=3697200):
    p = ET.Element(q(W, "p"))
    ppr = ET.SubElement(p, q(W, "pPr")); ET.SubElement(ppr, q(W, "jc")).set(q(W, "val"), "center")
    run = ET.SubElement(p, q(W, "r")); drawing = ET.SubElement(run, q(W, "drawing"))
    inline = ET.SubElement(drawing, q(WP, "inline"), {"distT":"0", "distB":"0", "distL":"0", "distR":"0"})
    ET.SubElement(inline, q(WP, "extent"), {"cx":str(cx), "cy":str(cy)})
    ET.SubElement(inline, q(WP, "docPr"), {"id":rel_id[3:], "name":name})
    graphic = ET.SubElement(inline, q(A, "graphic"))
    gd = ET.SubElement(graphic, q(A, "graphicData"), {"uri":"http://schemas.openxmlformats.org/drawingml/2006/picture"})
    pic = ET.SubElement(gd, q(PIC, "pic"))
    nv = ET.SubElement(pic, q(PIC, "nvPicPr")); ET.SubElement(nv, q(PIC, "cNvPr"), {"id":"0", "name":name}); ET.SubElement(nv, q(PIC, "cNvPicPr"))
    fill = ET.SubElement(pic, q(PIC, "blipFill")); ET.SubElement(fill, q(A, "blip"), {q(R, "embed"):rel_id}); stretch = ET.SubElement(fill, q(A, "stretch")); ET.SubElement(stretch, q(A, "fillRect"))
    sp = ET.SubElement(pic, q(PIC, "spPr")); xfrm = ET.SubElement(sp, q(A, "xfrm")); ET.SubElement(xfrm, q(A, "off"), {"x":"0", "y":"0"}); ET.SubElement(xfrm, q(A, "ext"), {"cx":str(cx), "cy":str(cy)}); geom = ET.SubElement(sp, q(A, "prstGeom"), {"prst":"rect"}); ET.SubElement(geom, q(A, "avLst"))
    return p


def normalize_with_python_docx(source, target):
    try:
        from docx import Document
    except ImportError:
        if not WINDOWS_PYTHON.exists() or shutil.which("wslpath") is None:
            raise RuntimeError("python-docx is required to normalize the final DOCX")
        win_source = subprocess.check_output(["wslpath", "-w", str(source)], text=True).strip()
        win_target = subprocess.check_output(["wslpath", "-w", str(target)], text=True).strip()
        subprocess.run([
            str(WINDOWS_PYTHON), "-c",
            "from docx import Document; import sys; Document(sys.argv[1]).save(sys.argv[2])",
            win_source, win_target,
        ], check=True)
    else:
        Document(source).save(target)


def main():
    with ZipFile(SOURCE) as zin:
        package = {name: zin.read(name) for name in zin.namelist()}
    root = ET.fromstring(package["word/document.xml"])
    body = root.find(q(W, "body"))
    sect = next((deepcopy(x) for x in reversed(list(body)) if x.tag == q(W, "sectPr")), None)
    for el in list(body): body.remove(el)

    rel_path = "word/_rels/document.xml.rels"
    rels = ET.fromstring(package[rel_path])
    for rid, filename in (("rId901", "figure1_cohort_flow.png"), ("rId902", "figure_calibration_5y_8y.png")):
        ET.SubElement(rels, q(REL, "Relationship"), {"Id":rid, "Type":"http://schemas.openxmlformats.org/officeDocument/2006/relationships/image", "Target":f"media/{filename}"})
        package[f"word/media/{filename}"] = (GENERATED / filename).read_bytes()
    package[rel_path] = ET.tostring(rels, encoding="utf-8", xml_declaration=True)
    lines = MARKDOWN.read_text(encoding="utf-8").splitlines()
    buf = []
    def flush():
        if buf: body.append(paragraph(" ".join(buf))); buf.clear()
    for line in lines:
        s = line.strip()
        if not s: flush(); continue
        if s.startswith("# "): flush(); body.append(paragraph(s[2:], "Title")); continue
        if s.startswith("## "):
            flush(); body.append(paragraph(s[3:], "Heading1", page_break=(s == "## References"))); continue
        if s.startswith("### "): flush(); body.append(paragraph(s[4:], "Heading2")); continue
        if s.startswith("**Table 1."):
            flush(); body.append(paragraph(s, keep_next=True)); body.append(table_from_csv(GENERATED/"table1_revised.csv", [3300,2400,3000])); continue
        if s.startswith("**Table 2."):
            flush(); body.append(paragraph(s, keep_next=True)); body.append(table_from_csv(GENERATED/"table2_revised.csv", [2350,2250,3500,1250], nowrap_columns=(0,))); continue
        if s.startswith("**Figure 1."):
            flush(); body.append(image_paragraph("rId901", "Figure 1 cohort flow", cy=3697200)); body.append(paragraph(s, keep_next=True)); continue
        if s.startswith("**Figure 2."):
            flush(); body.append(image_paragraph("rId902", "Figure 2 calibration", cy=2667000)); body.append(paragraph(s, keep_next=True)); continue
        if re.match(r"^\d+\. ", s): flush(); body.append(paragraph(s)); continue
        buf.append(s)
    flush()
    if sect is not None: body.append(sect)
    package["word/document.xml"] = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    with tempfile.NamedTemporaryFile(dir=TARGET.parent, suffix=".docx", delete=False) as tmp: temp = Path(tmp.name)
    try:
        with ZipFile(temp, "w", ZIP_DEFLATED) as zout:
            for name, data in package.items(): zout.writestr(name, data)
        # Normalize the handcrafted review package through python-docx. This
        # rewrites relationships/content types into an interoperable OOXML
        # package while preserving the manuscript content and layout.
        normalize_with_python_docx(temp, TARGET)
    finally:
        if temp.exists(): temp.unlink()


if __name__ == "__main__":
    main()
