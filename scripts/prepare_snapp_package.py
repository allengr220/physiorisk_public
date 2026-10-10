#!/usr/bin/env python3
"""Apply the two strictly scoped Snapp package updates."""

from pathlib import Path
from tempfile import NamedTemporaryFile
from zipfile import ZipFile
import os
import struct


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "submission" / "biogerontology"
MANUSCRIPT = PACKAGE / "PhysioRisk_Biogerontology_Manuscript.docx"

OLD_DATA_AVAILABILITY = (
    "NHANES data and public-use linked mortality files are publicly available from the National Center for Health "
    "Statistics. Analysis code, aggregate result tables, supplementary material, and reproducibility and provenance "
    "documentation are available at https://github.com/allengr220/physiorisk_public/. Participant-level analytic "
    "datasets and derived score files are not redistributed. Their construction and provenance are documented in "
    "the repository."
)

NEW_DATA_AVAILABILITY = (
    "NHANES 1999–2016 datasets used in this study are publicly available from the National Center for Health "
    "Statistics, Centers for Disease Control and Prevention, at https://www.cdc.gov/nchs/nhanes/. The 2019 Public-use "
    "Linked Mortality Files are publicly available from the National Center for Health Statistics at "
    "https://www.cdc.gov/nchs/data/datalinkage/public-use-linked-mortality-file-description.pdf. These public-use "
    "datasets do not have study-specific accession numbers or DOIs. Analysis code, aggregate result tables, "
    "supplementary material, and reproducibility and provenance documentation are available at "
    "https://github.com/allengr220/physiorisk_public/. Participant-level analytic datasets and derived score files "
    "are not redistributed. Their construction and provenance are documented in the repository."
)


def png_dimensions(data):
    if data[:16] != b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR":
        raise ValueError("Expected a PNG with an IHDR header")
    return struct.unpack(">II", data[16:24])


def main():
    figures = {
        "word/media/image1.png": (PACKAGE / "Fig1.png", (2700, 1680)),
        "word/media/image2.png": (PACKAGE / "Fig2.png", (2880, 1290)),
    }
    replacements = {}
    for member, (path, expected_dimensions) in figures.items():
        data = path.read_bytes()
        actual_dimensions = png_dimensions(data)
        if actual_dimensions != expected_dimensions:
            raise RuntimeError(f"Unexpected dimensions for {path}: {actual_dimensions}")
        replacements[member] = data

    with ZipFile(MANUSCRIPT) as source:
        infos = source.infolist()
        package = {info.filename: source.read(info.filename) for info in infos}

    document = package["word/document.xml"]
    old = OLD_DATA_AVAILABILITY.encode("utf-8")
    new = NEW_DATA_AVAILABILITY.encode("utf-8")
    if document.count(old) == 1 and document.count(new) == 0:
        document = document.replace(old, new)
    elif document.count(old) == 0 and document.count(new) == 1:
        pass
    else:
        raise RuntimeError("Neither the pre-Snapp nor Snapp data-availability state was found exactly once")
    package["word/document.xml"] = document
    package.update(replacements)

    with NamedTemporaryFile(dir=MANUSCRIPT.parent, suffix=".docx", delete=False) as handle:
        temporary = Path(handle.name)
    try:
        with ZipFile(temporary, "w") as target:
            for info in infos:
                target.writestr(info, package[info.filename])
        os.replace(temporary, MANUSCRIPT)
    finally:
        if temporary.exists():
            temporary.unlink()


if __name__ == "__main__":
    main()
