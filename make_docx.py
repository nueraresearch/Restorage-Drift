#!/usr/bin/env python3
"""Regenerate the .docx companions with fixed table geometry.

    python make_docx.py                     # both released documents
    python make_docx.py "Restorage Drift"   # one document

Pandoc writes every table column at an equal width and with no borders, so the
tables wrap into narrow strips and print as bare columns in Word. This script
converts the markdown, then sets a per-table column profile, fixes the table
layout, and draws horizontal rules only (booktabs style) to match the PDFs.
"""
import shutil
import subprocess
import sys
from pathlib import Path

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Twips

ROOT = Path(__file__).resolve().parent
# The documents in the release. Anything else is built by passing its name explicitly.
DOCS = [
    "Restorage Drift",
    "Iterative-Summarization Protocol",
]

# 6.5 in of text on Letter at 1 in margins, in twips.
TEXT_WIDTH = 9360

# Column profiles in twips, matched on the header row's text. Each sums to
# TEXT_WIDTH. Order matters: the first profile whose keywords all appear wins.
PROFILES = [
    (("example",),                          [1512, 1700, 1872, 2048, 2228]),
    (("arm", "manipulat"),                  [1872, 3168, 4320]),
    (("arm",),                              [1800, 2160, 5400]),
    (("minimal",),                          [5688, 1836, 1836]),
    (("quantity",),                         [1400, 3600, 4360]),
    (("role",),                             [2600, 1800, 4960]),
    (("cell",),                             [2400, 2200, 2400, 2360]),
]


def run(cmd):
    print("   ", " ".join(str(c) for c in cmd))
    return subprocess.run([str(c) for c in cmd], cwd=ROOT)


def insert_before(parent, el, successors):
    """Insert el in schema order, falling back to append if unknown."""
    try:
        parent.insert_element_before(el, *successors)
    except Exception:
        parent.append(el)


def frame(tbl, widths):
    """Fix layout, set column widths, add booktabs-style rules."""
    tblPr = tbl._tbl.tblPr

    tblW = tblPr.find(qn("w:tblW"))
    if tblW is None:
        tblW = OxmlElement("w:tblW")
        tblPr.insert(0, tblW)
    tblW.set(qn("w:type"), "dxa")
    tblW.set(qn("w:w"), str(TEXT_WIDTH))

    # fixed layout, so cell content cannot force a reflow
    layout = tblPr.find(qn("w:tblLayout"))
    if layout is None:
        layout = OxmlElement("w:tblLayout")
        insert_before(tblPr, layout, ("w:tblCellMar", "w:tblLook"))
    layout.set(qn("w:type"), "fixed")

    # horizontal rules only: rule above the table, below the header, below the body
    for old in tblPr.findall(qn("w:tblBorders")):
        tblPr.remove(old)
    borders = OxmlElement("w:tblBorders")
    for edge, val, sz in (("top", "single", 8), ("left", "none", 0),
                          ("bottom", "single", 8), ("right", "none", 0),
                          ("insideH", "none", 0), ("insideV", "none", 0)):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), val)
        el.set(qn("w:sz"), str(sz))
        el.set(qn("w:space"), "0")
        el.set(qn("w:color"), "auto")
        borders.append(el)
    insert_before(tblPr, borders,
                  ("w:shd", "w:tblLayout", "w:tblCellMar", "w:tblLook"))

    margins = OxmlElement("w:tblCellMar")
    for edge, w in (("top", 60), ("left", 100), ("bottom", 80), ("right", 100)):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:w"), str(w))
        el.set(qn("w:type"), "dxa")
        margins.append(el)
    insert_before(tblPr, margins, ("w:tblLook", "w:tblCaption"))

    for j, w in enumerate(widths):
        tbl.columns[j].width = Twips(w)
    for row in tbl.rows:
        for cell, w in zip(row.cells, widths):
            cell.width = Twips(w)

    # rule under the header row
    for cell in tbl.rows[0].cells:
        tcPr = cell._tc.get_or_add_tcPr()
        for old in tcPr.findall(qn("w:tcBorders")):
            tcPr.remove(old)
        tcb = OxmlElement("w:tcBorders")
        bottom = OxmlElement("w:bottom")
        bottom.set(qn("w:val"), "single")
        bottom.set(qn("w:sz"), "4")
        bottom.set(qn("w:space"), "0")
        bottom.set(qn("w:color"), "auto")
        tcb.append(bottom)
        insert_before(tcPr, tcb,
                      ("w:shd", "w:noWrap", "w:tcMar", "w:textDirection",
                       "w:tcFitText", "w:vAlign", "w:hideMark"))


def profile_for(tbl):
    header = " ".join(c.text.strip().lower() for c in tbl.rows[0].cells)
    ncols = len(tbl.columns)
    for keys, widths in PROFILES:
        if len(widths) == ncols and all(k in header for k in keys):
            return widths, "+".join(keys)
    equal = [TEXT_WIDTH // ncols] * ncols
    equal[-1] += TEXT_WIDTH - sum(equal)
    return equal, "equal (no profile)"


def main():
    pandoc = shutil.which("pandoc")
    if not pandoc:
        print("pandoc not found on PATH", file=sys.stderr)
        return 2

    wanted = sys.argv[1:] or DOCS
    for name in wanted:
        src = ROOT / f"{name}.md"
        dst = ROOT / f"{name}.docx"
        if not src.exists():
            print(f"missing source: {src.name}", file=sys.stderr)
            return 2
        print(f"\n=== {name} " + "=" * max(0, 50 - len(name)))
        if run([pandoc, src, "-o", dst]).returncode != 0:
            print(f"{name}: pandoc failed", file=sys.stderr)
            return 1

        doc = Document(str(dst))
        for i, tbl in enumerate(doc.tables):
            widths, why = profile_for(tbl)
            frame(tbl, widths)
            print(f"    table {i}: {len(tbl.columns)} cols, "
                  f"{[round(w / 1440, 2) for w in widths]} in  [{why}]")
        doc.save(str(dst))
        print(f"    -> {dst.name}, {len(doc.tables)} table(s) fixed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
