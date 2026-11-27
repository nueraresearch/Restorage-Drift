#!/usr/bin/env python3
"""Rebuild the whole paper in one command.

    python build.py                 # figures, preview, manuscript PDF, protocol PDF
    python build.py --skip-figures  # PDFs only
    python build.py --no-sheet      # skip the PNG contact sheet

Steps run in order; the manuscript does not rebuild if the figure step fails. The metadata
check runs before anything is built, so a .zenodo.json that would not deposit fails here.
"""
import hashlib
import json
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
ZENODO = ROOT / ".zenodo.json"

# Zenodo's controlled vocabularies for the fields below. A value outside them is rejected
# when the deposit is made, which is a slow way to find out; check_metadata() is the fast one.
ACCESS_RIGHTS = {"open", "embargoed", "restricted", "closed"}
UPLOAD_TYPES = {"publication", "poster", "presentation", "dataset", "image", "video",
                "software", "lesson", "physicalobject", "other"}
PUBLICATION_TYPES = {"annotationcollection", "book", "section", "conferencepaper",
                     "datamanagementplan", "article", "patent", "preprint", "deliverable",
                     "milestone", "proposal", "report", "softwaredocumentation",
                     "taxonomictreatment", "technicalnote", "thesis", "workingpaper",
                     "other"}
ORCID_PATTERN = re.compile(r"^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$")
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

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


def check_metadata():
    """What a Zenodo deposit needs from .zenodo.json, checked here rather than by Zenodo.

    Returns a list of problems; empty means the record would deposit as written. The keys
    are the legacy deposition fields, which is the dialect .zenodo.json is written in and
    the one Zenodo's GitHub integration reads, so a stricter reading of some other schema
    is not a defect this guard should reproduce.
    """
    try:
        meta = json.loads(ZENODO.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return [".zenodo.json is missing"]
    except json.JSONDecodeError as exc:
        return [f".zenodo.json is not valid JSON: {exc.msg} at line {exc.lineno} column {exc.colno}"]
    if not isinstance(meta, dict):
        return [".zenodo.json must contain a JSON object"]

    problems = []
    for key in ("title", "description", "publication_date", "access_right", "license", "upload_type"):
        value = meta.get(key)
        if not isinstance(value, str) or not value.strip():
            problems.append(f"{key} is required and must be a non-empty string")

    date = meta.get("publication_date")
    if isinstance(date, str) and date.strip() and not ISO_DATE.match(date):
        problems.append(f"publication_date must be YYYY-MM-DD, found {date!r}")

    access = meta.get("access_right")
    if isinstance(access, str) and access not in ACCESS_RIGHTS:
        problems.append(f"access_right must be one of {sorted(ACCESS_RIGHTS)}, found {access!r}")

    upload = meta.get("upload_type")
    if isinstance(upload, str) and upload not in UPLOAD_TYPES:
        problems.append(f"upload_type must be one of {sorted(UPLOAD_TYPES)}, found {upload!r}")

    publication = meta.get("publication_type")
    if upload == "publication" and not publication:
        problems.append("publication_type is required when upload_type is 'publication'")
    if isinstance(publication, str) and publication not in PUBLICATION_TYPES:
        problems.append(f"publication_type must be one of {sorted(PUBLICATION_TYPES)}, found {publication!r}")

    creators = meta.get("creators")
    if not isinstance(creators, list) or not creators:
        problems.append("creators is required and must be a non-empty list")
    else:
        for i, creator in enumerate(creators):
            if not isinstance(creator, dict):
                problems.append(f"creators[{i}] must be an object")
                continue
            if not str(creator.get("name", "")).strip():
                problems.append(f"creators[{i}].name is required")
            orcid = creator.get("orcid")
            if not isinstance(orcid, str) or not orcid.strip():
                problems.append(f"creators[{i}].orcid is required: it is what ties the author to the record")
            elif not ORCID_PATTERN.match(orcid):
                problems.append(f"creators[{i}].orcid is not an ORCID: {orcid!r}")
    return problems


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

    # Sections 7.1 and 9 each state derived numbers in several places, and four files
    # quote the word counts. Recompute all of it before spending a minute on figures.
    # Page counts need the PDFs, so that part waits until after the build.
    step("metadata")
    problems = check_metadata()
    if problems:
        for problem in problems:
            print(f"    - {problem}", file=sys.stderr)
        print("metadata would not deposit as written - not building", file=sys.stderr)
        return 1
    print("    .zenodo.json: required fields present")

    step("derived numbers")
    rc = run([sys.executable, ROOT / "check_thresholds.py", "--skip-pages"])
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

    # With the PDFs rebuilt, the page counts every file quotes can be checked as well.
    step("quoted counts")
    rc = run([sys.executable, ROOT / "check_thresholds.py"])
    if rc.returncode != 0:
        print("a quoted count disagrees with the built document", file=sys.stderr)
        return rc.returncode

    print(f"\nall builds finished in {time.time() - t0:.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
