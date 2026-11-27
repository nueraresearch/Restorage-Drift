#!/usr/bin/env python3
"""Rebuild the whole paper in one command.

    python build.py                 # figures, preview, manuscript PDF, protocol PDF
    python build.py --skip-figures  # PDFs only
    python build.py --no-sheet      # skip the PNG contact sheet

Steps run in order; the manuscript does not rebuild if the figure step fails.
"""
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANUSCRIPT = ROOT / "Restorage Drift.md"
PROTOCOL = ROOT / "Iterative-Summarization Protocol.md"
HEADER = ROOT / "fig-header.tex"


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
        print(f"    -> {out.name}" + (f", {n} pages" if n else ""))

    print(f"\nall builds finished in {time.time() - t0:.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
