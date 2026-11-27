#!/usr/bin/env python3
"""Rebuild the whole paper in one command.

    python build.py                 # figures, preview, manuscript PDF, protocol PDF
    python build.py --skip-figures  # PDFs only
    python build.py --no-sheet      # skip the PNG contact sheet

Steps run in order; the manuscript does not rebuild if the figure step fails.
"""
import hashlib
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANUSCRIPT = ROOT / "Restorage Drift.md"
PROTOCOL = ROOT / "Iterative-Summarization Protocol.md"
HEADER = ROOT / "fig-header.tex"

# Reproducible PDFs. pdfTeX stamps /CreationDate and /ModDate from the wall clock and
# derives the trailer /ID partly from the time, so two builds of the same sources
# differ. Pin the clock for the child processes (pdfTeX honours SOURCE_DATE_EPOCH),
# then replace the /ID with a digest of the finished file so it depends on content
# only. Override the epoch if a caller needs a different one.
BUILD_EPOCH = 1795737600  # 2026-11-27T00:00:00Z, the release date
ID_PATTERN = re.compile(rb"(/ID\s*\[\s*<)([0-9A-Fa-f]{32})(>\s*<)([0-9A-Fa-f]{32})(>\s*\])")


def step(title):
    print(f"\n=== {title} " + "=" * max(0, 60 - len(title)))


def run(cmd):
    print("   ", " ".join(str(c) for c in cmd[:3]), "...")
    return subprocess.run([str(c) for c in cmd], cwd=ROOT)


def pandoc(src, dst):
    return run([PANDOC, src, "-o", dst, "--pdf-engine=pdflatex",
                "--pdf-engine-opt=-interaction=nonstopmode",
                "--pdf-engine-opt=-halt-on-error",
                "--include-in-header", HEADER,
                "-V", "geometry:margin=1in", "-V", "fontsize=11pt"])


def normalise_id(pdf):
    """Replace the trailer /ID with an MD5 of the file itself, in place.

    Both hex strings are rewritten at their original length, so the cross-reference
    offsets stay valid and no other byte moves. Returns False if the trailer has no
    /ID in the expected form, which is worth reporting rather than passing over.
    """
    data = pdf.read_bytes()
    if not ID_PATTERN.search(data):
        return False
    zeroed = ID_PATTERN.sub(lambda m: m.group(1) + b"0" * 32 + m.group(3) + b"0" * 32 + m.group(5), data)
    digest = hashlib.md5(zeroed).hexdigest().encode("ascii")
    fixed = ID_PATTERN.sub(lambda m: m.group(1) + digest + m.group(3) + digest + m.group(5), data)
    if fixed != data:
        pdf.write_bytes(fixed)
    return True


def page_count(pdf):
    try:
        from pypdf import PdfReader
    except ImportError:
        return None
    try:
        return len(PdfReader(str(pdf)).pages)
    except Exception:
        return None


def main():
    global PANDOC
    skip_figs = "--skip-figures" in sys.argv
    PANDOC = shutil.which("pandoc")
    if not PANDOC:
        print("pandoc not found on PATH", file=sys.stderr)
        return 2
    if not MANUSCRIPT.exists():
        print(f"missing source: {MANUSCRIPT.name}", file=sys.stderr)
        return 2

    # Sections 7.1 and 9 each state derived numbers in several places. Recompute them
    # before spending a minute on figures.
    step("derived numbers")
    rc = run([sys.executable, ROOT / "check_thresholds.py"])
    if rc.returncode != 0:
        print("derived numbers disagree with their arithmetic - not building", file=sys.stderr)
        return rc.returncode

    os.environ.setdefault("SOURCE_DATE_EPOCH", str(BUILD_EPOCH))
    print(f"    SOURCE_DATE_EPOCH={os.environ['SOURCE_DATE_EPOCH']}")

    t0 = time.time()

    if not skip_figs:
        step("figures + preview")
        rc = run([sys.executable, ROOT / "figures" / "make_figures.py"])
        if rc.returncode != 0:
            print("figure build failed - stopping before the PDFs", file=sys.stderr)
            return rc.returncode

    for label, src in (("manuscript", MANUSCRIPT), ("protocol", PROTOCOL)):
        step(f"{label} PDF")
        out = src.with_suffix(".pdf")
        rc = pandoc(src, out)
        if rc.returncode != 0:
            print(f"{label} build failed", file=sys.stderr)
            return rc.returncode
        n = page_count(out)
        fixed = normalise_id(out)
        note = "" if fixed else "  (no /ID found to normalise)"
        print(f"    -> {out.name}" + (f", {n} pages" if n else "") + note)

    print(f"\nall builds finished in {time.time() - t0:.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
