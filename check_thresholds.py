#!/usr/bin/env python3
"""Check the protocol's derived numbers against the arithmetic that produces them.

Two blocks qualify. Section 7.1 states a count and two error rates per prediction, in a
table, a note and nine predictions that have to agree. Section 9 states call counts,
token estimates and band-share sensitivities that are all products of the design. Both
have drifted before, so build.py runs this first and refuses to make a PDF if it fails.

    python check_thresholds.py      # exit 0 when consistent, 1 with a report

ROWS is the specification for 7.1: unit count, the no-effect rate, the minimum effect,
and the two lines. alpha, beta and power are recomputed here from those four, so a
number written into the document cannot drift from the arithmetic behind it. The cost constants below play the same role for 9, and the prose that states them is anchored
too, so changing a replicate count in one place and not the other fails the check.

The word and page counts are checked the same way, against README, CHANGELOG,
RELEASE_NOTES and .zenodo.json.

The OSF registration draft is working material that is deliberately kept out of the
repository, so nothing else can see it drift from the protocol. check_registration_draft()
regenerates its figures from the same constants and runs only when the file is present. Pages come from the built PDFs, so build.py runs this
once before building (with --skip-pages, since the PDFs are about to be replaced) and
again afterwards to compare what was actually produced.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import subprocess
import sys
from math import comb
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROTOCOL = ROOT / "Iterative-Summarization Protocol.md"

# The design as Section 8 states it. Prediction 9's unit count is derived from these
# rather than typed in, because typing it in is what went wrong.
ITEMS = 40
CODED_REPLICATES = 3
CODED_CHAINS = ITEMS * CODED_REPLICATES   # 120
PAIRS = ITEMS // 2                        # 20

# --- Section 9 cost model ---------------------------------------------------------
# Every figure in the cost table is a product of these, so they are stated once here
# and the prose that introduces them is checked against them as well.
CELLS = 6                 # arm-cells, as the table's own row label says
REPLICATES = 10           # chains per item per condition
CYCLES = 10               # K
Q_BASE = 20               # probe samples per measurement
Q_EXT = 60                # extended draw when the estimate is near one half
BAND_SHARE = 0.20         # planning assumption for the adaptive rule
TOK_SUMMARY = 110
TOK_PROBE = 100
MINIMAL_ITEMS = 4
CODED_CYCLES = 10

COST_LABELS = ("Summarization calls", "Probe calls", "Total calls", "Approximate tokens")

# --- quoted counts ----------------------------------------------------------------
PAPER_MD = ROOT / "Restorage Drift.md"
PAPER_PDF = ROOT / "Restorage Drift.pdf"
S1_PDF = ROOT / "Iterative-Summarization Protocol.pdf"
LATEX_BLOCK = re.compile(r"^```\{=latex\}.*?^```", re.S | re.M)
NUMBER_WORDS = {w: n for n, w in enumerate(
    "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen "
    "fifteen sixteen seventeen eighteen nineteen twenty".split())}

ROWS = [
    # Prediction 1's null is one half because the prediction names the two answers it contrasts -
    # the record's assertion and the prior's preference - so a system with no re-storage effect is
    # exchangeable between them. .25 is Prediction 5a's null, where the contest is against all four
    # candidates and the foils are genuine possibilities. At .5 the old 26-of-40 line sat at .040.
    {"key": "1", "label": "1 Directionality", "n": ITEMS, "p0": 0.50, "p1": 0.75,
     "support": 28, "failure": 23,
     "text": ["at least 28 of 40 items", "at most 23 of 40"]},
    {"key": "5a", "label": "5a Attractor mode", "n": PAIRS, "p0": 0.25, "p1": 0.75,
     "support": 14, "failure": 9,
     "text": ["at least 14 of the 20 pairs", "At most 9 of 20"]},
    {"key": "5b", "label": "5b Pair ordering", "n": PAIRS, "p0": 1 / 3, "p1": 0.75,
     "support": 14, "failure": 9,
     "text": ["at least 14 of the 20 pairs", "At most 9 of 20"]},
    {"key": "7", "label": "7 Mode sensitivity", "n": ITEMS, "p0": 0.50, "p1": 0.80,
     "support": 28, "failure": 23,
     "text": ["at least 28 of 40 items", "Sign agreement in 23 or fewer"]},
    {"key": "9", "label": "9 Evidence lag", "n": CODED_CHAINS, "p0": 0.27, "p1": 0.80,
     "support": 90, "failure": 84,
     "text": ["at least 90 of the 120 coded chains", "84 or fewer is failure"]},
]

ALPHA_CEILING = 0.01
BETA_CEILING = 0.10
HOLM_FWER = 0.05         # family-wise error the four confirmatory hypotheses are held to
MIN_BAND = 0.04          # the note promises a band of at least 4% of the units
LOG_TOLERANCE = 0.05     # ~12% in ratio terms, for values quoted to two figures
# The 7.1 correction paragraph quotes its alphas to two significant figures (8.3e-3 for
# 8.294e-3), so half a unit in the last quoted digit is well under 1%. The table's own
# tolerance is a tenth of a decade, which is too wide here: at 12% a quoted 9.3e-3 would
# pass against a computed 8.29e-3, and that sentence is a claim about the line's size.
ALPHA_QUOTE_TOLERANCE = 0.01

NOTE_MARKER = "The error rates behind each line, by row:"
NOTE_END = "stated above."
TABLE_HEAD = "| Prediction | $n$ |"

SCI = r"([0-9]+(?:\.[0-9]+)?)\s*\\times\s*10\^\{(-?\d+)\}"
BOUND = r"<\s*10\^\{(-?\d+)\}"
DEC = r"(?<![\d.])\.(\d+)"
TOKEN = re.compile(f"{SCI}|{BOUND}|{DEC}")


def ge(n: int, p: float, k: int) -> float:
    return sum(comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1))


def le(n: int, p: float, k: int) -> float:
    return sum(comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k + 1))


def derived(row: dict) -> dict:
    n, p0, p1 = row["n"], row["p0"], row["p1"]
    s, f = row["support"], row["failure"]
    return {"alpha": ge(n, p0, s), "beta": le(n, p1, f), "power": ge(n, p1, s),
            "band": (s - f - 1) / n}


def numbers(segment: str) -> list[tuple[str, float]]:
    out = []
    for m in TOKEN.finditer(segment):
        if m.group(1):
            out.append(("point", float(m.group(1)) * 10 ** int(m.group(2))))
        elif m.group(3):
            out.append(("upper", 10 ** int(m.group(3))))
        else:
            out.append(("point", float("0." + m.group(4))))
    return out


def matches(kind: str, got: float, want: float) -> bool:
    if kind == "upper":                      # "< 10^-40": true only if below the bound
        return got < want
    if got <= 0 or want <= 0:
        return got == want
    return abs(math.log10(got) - math.log10(want)) <= LOG_TOLERANCE


def table_rows(text: str) -> dict[str, list[str]]:
    lines = text.splitlines()
    start = next((i for i, ln in enumerate(lines) if ln.startswith(TABLE_HEAD)), None)
    if start is None:
        raise ValueError("the 7.1 table header was not found")
    rows = {}
    for ln in lines[start + 2:]:
        if not ln.startswith("|"):
            break
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if len(cells) == 7:
            rows[cells[0]] = cells
    return rows


def note_segments(text: str) -> dict[str, str]:
    i = text.index(NOTE_MARKER)
    # The per-row list ends where the summary sentence begins; otherwise the last row
    # swallows "the .01 and .10 ceilings" and reports 0.1 as its beta.
    end = text.find("The largest", i)
    j = end if end != -1 else text.index(NOTE_END, i)
    parts = re.split(r"\*\*([0-9]+[ab]?)\*\*", text[i:j])
    return {parts[k]: parts[k + 1] for k in range(1, len(parts) - 1, 2)}


def calls(items: int) -> int:
    """Chains times cycles: one summarization, and one measurement, per cycle."""
    return CELLS * items * CYCLES * REPLICATES


def band_samples(share: float) -> float:
    return Q_BASE + share * (Q_EXT - Q_BASE)


def cell_value(cell: str) -> float:
    raw = cell.replace(",", "").strip()
    return float(raw[:-1]) * 1e6 if raw.endswith("M") else float(raw)


def cost_rows(text: str) -> dict[str, list[str]]:
    rows = {}
    for line in text.splitlines():
        if not line.startswith("| "):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 3 and cells[0].startswith(COST_LABELS):
            rows[cells[0]] = cells[1:]
    return rows


def holm_steps(fwer: float = HOLM_FWER, members: int = 4) -> list[str]:
    """The Holm thresholds, derived rather than typed: .0125, .0167, .025, .05."""
    return [f"{fwer / (members - i):.4f}"[1:].rstrip("0").rstrip(".") for i in range(members)]


def check_multiplicity(text: str) -> list[str]:
    """Holm over the four confirmatory hypotheses: the step thresholds are arithmetic.

    Four hypotheses at a family-wise .05 give steps .0125, .0167, .025 and .05. All four
    are derived here, so a hand-edited step, a family that silently gains a member, or a
    table that forgets the correction cannot pass.
    """
    fwer, members = HOLM_FWER, 4
    steps = holm_steps(fwer, members)
    out = []

    # Scope to the rule's own paragraph: a step quoted anywhere else in the protocol is not
    # the correction, and a wrong step must not be masked by a coincidental match.
    start = text.find("**Multiplicity.**")
    rule = text[start:text.find("\n\n", start)] if start != -1 else ""
    if not rule:
        return ["Section 7: the multiplicity paragraph is missing"]
    for step in steps:
        if step not in rule:
            out.append(f"Section 7: the Holm step {step} is missing from the multiplicity rule")
    for phrase, why in (
        ("one family of four hypotheses", "the family's composition"),
        ("intersection-union", "why 5a and 5b count once"),
    ):
        if phrase not in rule:
            out.append(f"Section 7: the multiplicity statement lost {why}")
    # The claim that the table is conservative lives in 7.1, and must keep that form: the
    # phrase "lower bound" alone also occurs about a count line and would mask its removal.
    if "every power in the table is a lower bound" not in text:
        out.append("Section 7.1: the statement that the table's powers are lower bounds is missing")
    return out


def check_screen(text: str) -> list[str]:
    """The contamination screen is the only exclusion rule; its arithmetic can drift too.

    Four candidates, q = 20 draws, one-sided at .05: the rejection region starts at the
    smallest count whose binomial tail falls under .05. Those three inputs produce the
    threshold and the probability quoted in Section 3, so both are recomputed here.
    """
    n, p = 20, 0.25

    def upper(k):
        return sum(comb(n, i) * p**i * (1 - p) ** (n - i) for i in range(k, n + 1))

    reach = min(k for k in range(1, n + 1) if upper(k) <= 0.05)   # 9 of 20, p = .041
    tail = f"{upper(reach):.3f}"[1:]
    out = []
    for phrase, why in (
        ("Binomial}(20, 1/4)", "the binomial basis"),
        (f"{reach} or more of the {n} reconstructions", "the rejection threshold"),
        (tail, "the probability chance alone assigns that threshold"),
        (f"{reach - 1} or fewer", "the retention rule"),
        ("`screen`: `{recovered, q, passes}`", "the ground_truth field"),
    ):
        if phrase not in text:
            out.append(f"Section 3: the contamination screen lost {why} ({phrase!r})")
    return out


def check_costs(text: str) -> list[str]:
    """Recompute Section 9 from the design and compare every stated figure."""
    out: list[str] = []
    flat = " ".join(text.split())
    rows = cost_rows(text)
    q = band_samples(BAND_SHARE)
    c_min, c_full = calls(MINIMAL_ITEMS), calls(ITEMS)

    def tokens(c: int) -> float:
        return c * TOK_SUMMARY + c * q * TOK_PROBE

    def row(label: str, expected: tuple[float, float]) -> None:
        cells = next((c for k, c in rows.items() if k.startswith(label)), None)
        if cells is None:
            out.append(f"cost table: no row starting {label!r}")
            return
        for side, cell, want in zip(("minimal", "full"), cells, expected):
            try:
                got = cell_value(cell)
            except ValueError:
                out.append(f"cost table {label} ({side}): {cell!r} is not a number")
                continue
            # Counts are exact; only the "7.0M" token cells are rounded, so only they
            # get a percentage tolerance. Anything else must match the count itself.
            tol = 0.015 * want if cell.strip().endswith("M") else 0.5
            if abs(got - want) > tol:
                out.append(f"cost table {label} ({side}): reads {cell}, "
                           f"computes {want:,.0f}")

    row("Summarization calls", (c_min, c_full))
    row("Probe calls", (c_min * q, c_full * q))
    row("Total calls", (c_min * (1 + q), c_full * (1 + q)))
    row("Approximate tokens", (tokens(c_min), tokens(c_full)))

    probe_label = next((k for k in rows if k.startswith("Probe calls")), "")
    if f"{q:g} samples" not in probe_label:
        out.append(f"cost table: the probe row does not name {q:g} samples per measurement")

    # the arithmetic the adaptive rule is introduced with: 20 + 0.2 x 40 = 28
    eq = re.search(r"\$%d \+ ([0-9.]+) \\times %d = (\d+)\$" % (Q_BASE, Q_EXT - Q_BASE), text)
    if not eq:
        out.append("Section 9: the probe-rule equation was not found")
    else:
        share_seen, total_seen = float(eq.group(1)), int(eq.group(2))
        if abs(share_seen - BAND_SHARE) > 1e-9:
            out.append(f"probe rule: the equation uses a {share_seen:g} band share, "
                       f"the model {BAND_SHARE:g}")
        if total_seen != q:
            out.append(f"probe rule: the equation totals {total_seen}, computes {q:g}")

    # the design sentence the whole table rests on
    for anchor in (f"$m = {REPLICATES}$", f"$K = {CYCLES}$", f"$q = {Q_BASE}$",
                   f"{CELLS} arm-cells", f"about {TOK_SUMMARY} per summary",
                   f"about {TOK_PROBE} per probe"):
        if anchor not in flat:
            out.append(f"Section 9: expected the design statement {anchor!r}")

    # band-share sensitivities, the two named plus the ceiling
    for share in (0.10, 0.30, 1.0):
        s = band_samples(share)
        expected = f"{c_min * s:,.0f} and {c_full * s:,.0f}"
        if expected not in flat:
            where = "every measurement" if share == 1.0 else f"{share:.0%} in the band"
            out.append(f"sensitivity ({where}): expected {expected!r}")

    # probe share of calls and tokens, quoted to the nearest percent
    share_calls = 100 * q / (1 + q)
    share_tokens = 100 * (c_full * q * TOK_PROBE) / tokens(c_full)
    m = re.search(r"Probes are about (\d+)% of both calls and tokens", flat)
    if not m:
        out.append("Section 9: the probe-share sentence was not found")
    else:
        for name, value in (("calls", share_calls), ("tokens", share_tokens)):
            if abs(value - int(m.group(1))) > 1.0:
                out.append(f"probe share of {name}: the sentence says {m.group(1)}%, "
                           f"computes {value:.1f}%")

    # the coding cost in the same section is derived the same way
    def texts(items: int) -> int:
        return CELLS * items * CODED_REPLICATES * CODED_CYCLES

    t_min, t_full = texts(MINIMAL_ITEMS), texts(ITEMS)
    for needle in (f"{t_min:,} stored texts", f"{2 * t_min:,} codings",
                   f"{t_full:,} texts scored twice", f"{2 * t_full:,} codings",
                   f"about {2 * t_min // 60} and {2 * t_full // 60} hours"):
        if needle not in flat:
            out.append(f"coding cost: expected {needle!r}")

    print(f"    {'cost':8s} {'minimal':>10s} {'full':>12s}")
    print(f"    {'calls':8s} {c_min:10,d} {c_full:12,d}")
    print(f"    {'probes':8s} {c_min * q:10,.0f} {c_full * q:12,.0f}")
    print(f"    {'tokens':8s} {tokens(c_min) / 1e6:9.1f}M {tokens(c_full) / 1e6:11.1f}M")
    print(f"    probes are {share_calls:.1f}% of calls, {share_tokens:.1f}% of tokens")
    return out


def word_count(path: Path) -> int:
    """Whitespace-separated tokens once the LaTeX layout blocks are removed.

    Deliberately locale-independent. GNU wc -w splits multibyte text differently under
    LC_ALL=C: it counts 5,142 for S1 where C.UTF-8 counts 5,167, and the published
    figures had come from the C-locale run. A quoted count should not depend on the
    shell's locale, so this is the definition the documents are held to.
    """
    kept: list[str] = []
    inside = False
    for line in path.read_text(encoding="utf-8").splitlines(keepends=True):
        if inside:
            inside = "```" not in line
            continue
        if "```{=latex}" in line:
            inside = True
            continue
        kept.append(line)
    return len("".join(kept).split())


def page_count(pdf: Path) -> int | None:
    try:
        from pypdf import PdfReader
    except ImportError:
        return None
    try:
        return len(PdfReader(str(pdf)).pages)
    except Exception:
        return None


def check_quotes(include_pages: bool) -> list[str]:
    """Compare every quoted word and page count outside the documents with the source."""
    out: list[str] = []
    words = {"paper": word_count(PAPER_MD), "S1": word_count(PROTOCOL)}
    pages: dict[str, int | None] = {"paper": None, "S1": None}
    if include_pages:
        pages = {"paper": page_count(PAPER_PDF), "S1": page_count(S1_PDF)}
        if None in pages.values():
            print("    (page counts unavailable - PDFs not built or pypdf missing)")
    else:
        print("    (page counts skipped: the PDFs are about to be rebuilt)")

    def read(name: str) -> str:
        path = ROOT / name
        if not path.exists():
            out.append(f"{name}: missing")
            return ""
        return path.read_text(encoding="utf-8")

    def figure(where: str, label: str, seen: str, want: int, unit: str) -> None:
        try:
            value = int(seen.replace(",", ""))
        except ValueError:
            out.append(f"{where}: {label} {unit} reads {seen!r}")
            return
        if value != want:
            out.append(f"{where}: {label} says {value:,} {unit}, the source has {want:,}")

    readme = read("README.md")
    m = re.search(r"The theory paper, (\d+) pp, ([\d,]+) words", readme)
    if not m:
        out.append("README.md: the paper's \"N pp, N words\" line was not found")
    else:
        figure("README.md", "paper", m.group(2), words["paper"], "words")
        if pages["paper"]:
            figure("README.md", "paper", m.group(1), pages["paper"], "pp")
    m = re.search(r"Current count: ([\d,]+) words", readme)
    if not m:
        out.append("README.md: the current word count line was not found")
    else:
        figure("README.md", "current count", m.group(1), words["paper"], "words")

    notes = read("RELEASE_NOTES.md")
    m = re.search(r"the theory paper, (\d+) pp, ([\d,]+) words", notes)
    if not m:
        out.append("RELEASE_NOTES.md: the paper line was not found")
    else:
        figure("RELEASE_NOTES.md", "paper", m.group(2), words["paper"], "words")
        if pages["paper"]:
            figure("RELEASE_NOTES.md", "paper", m.group(1), pages["paper"], "pp")
    m = re.search(r"the test protocol, (\d+) pp", notes)
    if not m:
        out.append("RELEASE_NOTES.md: the S1 page line was not found")
    elif pages["S1"]:
        figure("RELEASE_NOTES.md", "protocol", m.group(1), pages["S1"], "pp")

    raw = read(".zenodo.json")
    try:
        description = json.loads(raw)["description"]
    except Exception as exc:
        out.append(f".zenodo.json: {exc}")
        description = ""
    m = re.search(r"Theory paper \((\d+) pp, ([\d,]+) words\)", description)
    if not m:
        out.append(".zenodo.json: the description's paper figures were not found")
    else:
        figure(".zenodo.json", "paper", m.group(2), words["paper"], "words")
        if pages["paper"]:
            figure(".zenodo.json", "paper", m.group(1), pages["paper"], "pp")
    m = re.search(r"(?:a|an) ([a-z]+)-page test protocol", description)
    if not m:
        out.append(".zenodo.json: the S1 page phrase was not found")
    elif pages["S1"]:
        spelled = NUMBER_WORDS.get(m.group(1))
        if spelled is None:
            out.append(f".zenodo.json: cannot read the page number {m.group(1)!r}")
        elif spelled != pages["S1"]:
            out.append(f".zenodo.json: says {m.group(1)}-page, the protocol has {pages['S1']} pp")

    # CHANGELOG keeps history, so only its latest summary line is a current claim.
    history = re.findall(
        r"The paper is ([\d,]+)\s+words\s+/\s+(\d+)\s+pp[^;]*;\s*S1 is ([\d,]+)\s+words\s+/\s+(\d+)\s+pp",
        read("CHANGELOG.md"))
    if not history:
        out.append("CHANGELOG.md: the current summary line was not found")
    else:
        wp, pp, ws, ps = history[-1]
        figure("CHANGELOG.md", "paper", wp, words["paper"], "words")
        figure("CHANGELOG.md", "protocol", ws, words["S1"], "words")
        if pages["paper"]:
            figure("CHANGELOG.md", "paper", pp, pages["paper"], "pp")
        if pages["S1"]:
            figure("CHANGELOG.md", "protocol", ps, pages["S1"], "pp")

    for label in ("paper", "S1"):
        shown = "" if pages[label] is None else f", {pages[label]} pp"
        print(f"    {label:8s} {words[label]:6,d} words{shown}")
    return out


# --- the registration draft ----------------------------------------------------------
# Working material, untracked and outside the archive, so no other check sees it. It has
# drifted from S1 twice: an alpha of .05 where the protocol says .01, and a Holm family
# of nine where the protocol has four. Every figure below is regenerated from the
# constants that hold the protocol (ROWS, MINIMAL_ITEMS, ITEMS, the Section 9 design),
# and every number the draft states must be claimed by one of the rules here - a number
# no rule claims is itself an error, which is what catches a third drift being written
# in rather than merely repeated.
DRAFT = ROOT / "Registration Fields Draft.md"

# Section references and version strings are not figures. They are masked before the
# coverage pass, so only numbers making a claim have to survive it.
DRAFT_STRUCTURAL = (
    r"Sections? 1–9",
    r"Sections? \d+(?:\.\d+)?(?:, \d+(?:\.\d+)?)*(?: and \d+(?:\.\d+)?)?",
    r"v\d+\.\d+\.\d+",
    r"\d+ November \d{4}",
    r"SHA-256",
    r"UTF-8",
    r"5a|5b",
    r"Prediction \d+",
    r"items\.[a-z]+\.jsonl",
    r"\bS1\b",
)


# The text this record is built from. Binary artifacts are excluded on purpose: a .pdf and
# a .docx carry control bytes legitimately.
TEXT_FILES = (
    "Restorage Drift.md", "Iterative-Summarization Protocol.md", "CHANGELOG.md",
    "DEPOSIT.md", "README.md", "RELEASE_NOTES.md", ".zenodo.json", ".gitignore",
    ".gitattributes", "LICENSE", "build.py", "check_thresholds.py", "make_docx.py",
    "fig-header.tex", "figures/make_figures.py",
)


def check_no_control_characters() -> list[str]:
    """No stray control bytes in the prose this release is built from.

    A backslash typed inside a heredoc can arrive as the character it names - ``\\a`` is
    0x07 - and the damage is invisible in a diff, survives a read of the paragraph, and
    surfaces only in the built file, where LaTeX refuses it. Repairing the bytes is not
    enough: this is what stops the next edit from writing them again.
    """
    out: list[str] = []
    for name in TEXT_FILES:
        path = ROOT / name
        if not path.exists():
            continue
        # A tab belongs in Python indentation and nowhere in prose. Allowing 0x09 in the
        # first version of this check is what hid the second casualty: ``\times`` had
        # become ``<TAB>imes`` and passed as "no control bytes".
        allowed = {0x0A, 0x09} if name.endswith(".py") else {0x0A}
        bad = sorted({b for b in path.read_bytes() if b < 0x20 and b not in allowed})
        if bad:
            out.append(f"{name}: control byte(s) {', '.join(hex(b) for b in bad)}")
    return out


def check_registration_draft() -> list[str]:
    """Hold the registration draft's figures to the protocol, when the draft is here.

    The draft is gitignored and absent from a clean clone, so a missing file is a skip
    with a note rather than a failure: the deposit must still build on a machine that does
    not have the author's working files. When it is present, every number it states is
    either checked against a constant the protocol is also held to, or reported.
    """
    if not DRAFT.exists():
        print("    (registration draft absent - skipped; it is not part of the archive)")
        return []
    draft = DRAFT.read_text(encoding="utf-8")
    protocol = PROTOCOL.read_text(encoding="utf-8")
    out: list[str] = []
    masked = draft
    rows = {r["key"]: r for r in ROWS}

    # DEPOSIT.md names the registered text by content, which is the only tie the record can
    # carry to a file it does not contain. A stale digest there would be worse than none,
    # so it is compared whenever the file is here to compare against - and only then, since
    # a clean clone has neither the draft nor any way to verify it.
    deposit = ROOT / "DEPOSIT.md"
    if deposit.exists():
        recorded = deposit.read_text(encoding="utf-8")
        digest = hashlib.sha256(DRAFT.read_bytes()).hexdigest()
        size = DRAFT.stat().st_size
        found = re.search(r"\| SHA-256 \| `([0-9a-f]{64})` \|", recorded)
        if not found:
            out.append("DEPOSIT.md: the draft's SHA-256 is not recorded")
        elif found.group(1) != digest:
            out.append(f"DEPOSIT.md: records the draft as {found.group(1)[:16]}..., "
                       f"the file hashes to {digest[:16]}...")
        found = re.search(r"\| Bytes \| ([\d,]+) \|", recorded)
        if not found:
            out.append("DEPOSIT.md: the draft's byte size is not recorded")
        elif int(found.group(1).replace(",", "")) != size:
            out.append(f"DEPOSIT.md: records {found.group(1)} bytes for the draft, "
                       f"the file is {size:,}")

        # The reproduce block prints the same two values as comments a reader is meant to
        # compare against. They drifted once while the table above them was correct, so
        # they are held to the file as well.
        m = re.search(r'sha256sum "Registration Fields Draft\.md"\s+# ([0-9a-f]{8})',
                      recorded)
        if not m:
            out.append("DEPOSIT.md: the reproduce block no longer prints the digest")
        elif not digest.startswith(m.group(1)):
            out.append(f"DEPOSIT.md: the reproduce block prints {m.group(1)}..., "
                       f"the file hashes to {digest[:8]}...")
        m = re.search(r'wc -c < "Registration Fields Draft\.md"\s+# (\d+)', recorded)
        if not m:
            out.append("DEPOSIT.md: the reproduce block no longer prints the byte count")
        elif int(m.group(1)) != size:
            out.append(f"DEPOSIT.md: the reproduce block prints {m.group(1)} bytes, "
                       f"the file is {size:,}")

    def take(label: str, pattern: str) -> list[str] | None:
        nonlocal masked
        m = re.search(pattern, draft)
        masked = re.sub(pattern, " ", masked)
        if not m:
            out.append(f"draft: {label} was not found")
            return None
        return list(m.groups()) or [m.group(0)]

    def same(label: str, pattern: str, want: str, tol: float | None = None) -> None:
        got = take(label, pattern)
        if got is None:
            return
        value = got[0]
        if tol is None:
            if value != want:
                out.append(f"draft: {label} reads {value!r}, the protocol gives {want!r}")
            return
        try:
            seen = float(value.replace(",", ""))
        except ValueError:
            out.append(f"draft: {label} reads {value!r}, which is not a number")
            return
        if abs(seen - float(want.replace(",", ""))) > tol:
            out.append(f"draft: {label} reads {value}, the protocol gives {want}")

    max_alpha = max(derived(r)["alpha"] for r in ROWS)
    max_beta = max(derived(r)["beta"] for r in ROWS)

    # 1. the error ceilings, and the maxima Section 7.1's note reports
    same("the per-row alpha ceiling", r"no-effect rate at \$\\alpha \\leq (\.\d+)",
         f"{ALPHA_CEILING:.2f}"[1:])
    same("the beta ceiling", r"keeps \$\\beta \\leq (\.\d+)", f"{BETA_CEILING:.2f}"[1:])
    same("the largest alpha", r"largest achieved \$\\alpha\$ is (\.\d+)",
         f"{max_alpha:.4f}"[1:], tol=5e-5)
    # The note quotes the maxima to three decimals and the draft follows it, so that is
    # the precision this pair is held to; the old value is far outside it either way.
    same("the largest beta", r"largest \$\\beta\$ is (\.\d+)",
         f"{max_beta:.4f}"[1:], tol=5e-4)

    # 2. the correction: four steps, one family, and who is outside it
    steps = take("the Holm thresholds",
                 r"compared with (\.\d+), then (\.\d+), (\.\d+) and (\.\d+)")
    if steps is not None and steps != holm_steps():
        out.append(f"draft: the Holm thresholds read {', '.join(steps)}, "
                   f"the protocol's family of four gives {', '.join(holm_steps())}")
    level = f"{HOLM_FWER:.2f}"[1:]
    same("the family-wise error", r"family-wise \$\\alpha = (\.\d+)\$", level)
    if f"family-wise error at {level}" not in protocol:
        out.append("Section 7: the multiplicity rule no longer holds the family-wise "
                   f"error at {level}")
    fam = take("the family's membership",
               r"one family of four hypotheses — (\d+), (\d+), (\d+) and (\d+)")
    members = sorted({r["key"][0] for r in ROWS})
    if fam is not None and list(fam) != members:
        out.append(f"draft: the family is listed as {'/'.join(fam)}, "
                   f"the count-based rows are {'/'.join(members)}")
    for phrase in (r"intersection-union",
                   r"Predictions 2, 3 and 6 are decided by hazard ratios",
                   r"4 and 8 are tolerance lines"):
        if not re.search(phrase, draft):
            out.append(f"draft: the correction's scope lost {phrase!r}")
        masked = re.sub(phrase, " ", masked)

    # 3. the five count lines, parsed as claims and compared to the rows themselves
    start = draft.find("**Criteria in counts.**")
    para = draft[start:draft.find("\n\n", start)] if start != -1 else ""
    if not para:
        out.append("draft: the criteria-in-counts paragraph was not found")
    else:
        expected = {"1": rows["1"], "5": rows["5a"], "7": rows["7"], "9": rows["9"]}
        if (rows["5a"]["support"], rows["5a"]["n"]) != (rows["5b"]["support"], rows["5b"]["n"]):
            out.append("draft: Prediction 5 is quoted as one line, but 5a and 5b differ")
        body = para.split(":", 1)[1] if ":" in para else ""
        seen: set[str] = set()
        for part in re.split(r";\s*(?=Prediction )", body):
            key = re.search(r"Prediction (\d+)", part)
            if key is None:
                continue
            k = key.group(1)
            seen.add(k)
            row = expected.get(k)
            if row is None:
                out.append(f"draft: the counts paragraph quotes Prediction {k}, "
                           f"which is not one of the five count-based rows")
                continue
            nums = re.search(r"(\d+) of (?:the )?(\d+)", part)
            fail = re.search(r"(\d+) or fewer", part)
            if nums is None or fail is None:
                out.append(f"draft: the line for Prediction {k} has no support or failure count")
                continue
            if (int(nums.group(1)), int(nums.group(2))) != (row["support"], row["n"]):
                out.append(f"draft: Prediction {k} support reads {nums.group(1)} of "
                           f"{nums.group(2)}, the protocol has {row['support']} of {row['n']}")
            if int(fail.group(1)) != row["failure"]:
                out.append(f"draft: Prediction {k} failure reads {fail.group(1)}, "
                           f"the protocol has {row['failure']}")
        for k in sorted(set(expected) - seen):
            out.append(f"draft: Prediction {k} is missing from the counts paragraph")
        masked = masked.replace(para, " ")

    # 4. the design: slice size, full run, and the range of unit counts
    word = take("the minimal slice's item count", r"minimal slice is (\w+) items")
    if word is not None:
        spelled = NUMBER_WORDS.get(word[0])
        if spelled is None:
            out.append(f"draft: cannot read the slice size {word[0]!r}")
        elif spelled != MINIMAL_ITEMS:
            out.append(f"draft: the minimal slice is {word[0]} items, "
                       f"Section 9 makes it {MINIMAL_ITEMS}")
    same("the full run's item count", r"(\d+)-item full run", str(ITEMS))
    span = take("the range of unit counts", r"count on (\d+) to (\d+) units")
    if span is not None:
        want = (str(min(r["n"] for r in ROWS)), str(max(r["n"] for r in ROWS)))
        if tuple(span) != want:
            out.append(f"draft: the unit counts span {span[0]} to {span[1]}, "
                       f"the protocol's rows run {want[0]} to {want[1]}")

    # 5. the ceiling a Holm step is compared against, the interval level, the binomial
    same("the ceiling clearing a Holm step is compared against",
         r"clearing (\.\d+) but not its step", f"{ALPHA_CEILING:.2f}"[1:])
    same("the interval level", r"with (\d+)% intervals", "95")
    if "95% intervals" not in draft:
        out.append("draft: the 95% interval level is stated without its scope")
    binom = take("the screen's binomial", r"Binomial\}\((\d+), 1/(\d+)\)")
    if binom is not None and (int(binom[0]), int(binom[1])) != (Q_BASE, 4):
        out.append(f"draft: the screen is modelled as Binomial({binom[0]}, 1/{binom[1]}), "
                   f"Section 3 uses Binomial({Q_BASE}, 1/4)")

    # 6. the uniformity p the slice paragraph quotes, and the probe extension
    same("the four-item unanimity p", r"gives \$p = (\.\d+)\$",
         f"{ge(MINIMAL_ITEMS, rows['1']['p0'], MINIMAL_ITEMS):.4f}"[1:], tol=5e-5)
    ext = take("the probe extension", r"(\d+)-to-(\d+) probe extension")
    if ext is not None and tuple(ext) != (str(Q_BASE), str(Q_EXT)):
        out.append(f"draft: the probe extension reads {ext[0]}-to-{ext[1]}, "
                   f"Section 9 extends {Q_BASE} to {Q_EXT}")

    # 7. the contamination screen, recomputed exactly as check_screen() recomputes it
    nb, p_cand = Q_BASE, 1 / 4

    def upper(k: int) -> float:
        return sum(comb(nb, i) * p_cand**i * (1 - p_cand) ** (nb - i) for i in range(k, nb + 1))

    reach = min(k for k in range(1, nb + 1) if upper(k) <= 0.05)
    same("the screen's draws", r"\$q = (\d+)\$ draws", str(nb))
    same("the candidate count's chance rate", r"chance is \$1/(\d+)\$", str(4))
    cut = take("the screen threshold", r"discarded when (\d+) or more of the (\d+)")
    if cut is not None and (int(cut[0]), int(cut[1])) != (reach, nb):
        out.append(f"draft: the screen discards at {cut[0]} of {cut[1]}, "
                   f"Section 3 discards at {reach} of {nb}")
    same("the screen's tail probability", r"probability (\.\d+)",
         f"{upper(reach):.3f}"[1:], tol=5e-5)
    same("the screen's retention rule", r"retained at (\d+) or fewer", str(reach - 1))

    # 8. the call count the model-identity paragraph sizes the snapshot against
    full_calls = calls(ITEMS) * (1 + band_samples(BAND_SHARE))
    same("the full run's call count", r"about ([\d,]+) calls", f"{full_calls:,.0f}",
         tol=0.02 * full_calls)

    # 9. the exchangeability rate Prediction 5's ordering clause is counted against
    rate = take("the ordering clause's no-effect rate", r"\$(\d)/(\d)\$")
    if rate is not None and abs(int(rate[0]) / int(rate[1]) - rows["5b"]["p0"]) > 1e-9:
        out.append(f"draft: the ordering clause is counted against {rate[0]}/{rate[1]}, "
                   f"the protocol's rate for 5b is {rows['5b']['p0']:.4f}")

    # 10. a value S1 does not fix must still be marked as a proposal, not stated as fact
    i = draft.find("If more than 10%")
    if i == -1:
        out.append("draft: the 10% chain-exclusion threshold was not found")
    else:
        j = draft.find(". ", i)
        if "[default]" not in draft[i:j if j != -1 else len(draft)]:
            out.append("draft: the 10% exclusion threshold is stated without [default]")
    masked = re.sub(r"more than 10%", " ", masked)

    # 11. coverage: anything numeric left over is a figure with no protocol behind it
    rest = masked
    for pat in DRAFT_STRUCTURAL:
        rest = re.sub(pat, " ", rest)
    for token in sorted(set(re.findall(r"\d+(?:[.,]\d+)*", rest))):
        i = rest.find(token)
        near = " ".join(rest[max(0, i - 30):i + 30].split())
        out.append(f"draft: the figure {token!r} is not checked against the protocol "
                   f"[near: {near!r}] - add a rule, or mark it [default] if S1 does not fix it")

    if not out:
        print("    registration draft: figures match the protocol")
    return out


# --- the deposit inventory ---------------------------------------------------------------
# DEPOSIT.md's table is the only place in the record that claims what the archive contains,
# and it was verified by hand on every release pass. The table describes the *tagged* tree,
# not the working tree: on main after a release it should keep describing the tag, so the
# comparison is against the ref its own reproduce block names.
DEPOSIT_DOC = ROOT / "DEPOSIT.md"


def check_deposit_inventory() -> list[str]:
    """The inventory table, its total row and the sentence above it must match the tag."""
    if not DEPOSIT_DOC.exists():
        print("    (no DEPOSIT.md - inventory not checked)")
        return []
    text = DEPOSIT_DOC.read_text(encoding="utf-8")
    m = re.search(r"git ls-tree -r --long (\S+)", text)
    ref = m.group(1) if m else "v1.0.0"
    if subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=ROOT,
                      capture_output=True).returncode != 0:
        print("    (not a git checkout - inventory not checked against a tag)")
        return []
    listing = subprocess.run(["git", "ls-tree", "-r", "--long", ref], cwd=ROOT,
                             capture_output=True, text=True)
    if listing.returncode != 0:
        print(f"    ({ref} is not in this clone - inventory not checked)")
        return []

    tree: dict[str, int] = {}
    for line in listing.stdout.splitlines():
        meta, path = line.split("\t", 1)
        tree[path] = int(meta.split()[3])
    rows = {m.group(1): int(m.group(2).replace(",", ""))
            for m in re.finditer(r"^\| `([^`]+)` \| ([\d,]+) \|$", text, re.M)}

    out: list[str] = []
    if not rows:
        return ["DEPOSIT.md: the inventory table was not found"]
    for path in sorted(set(rows) | set(tree)):
        if path not in tree:
            out.append(f"DEPOSIT.md: lists {path}, which {ref} does not contain")
        elif path not in rows:
            out.append(f"DEPOSIT.md: does not list {path}, which {ref} contains")
        elif rows[path] != tree[path]:
            out.append(f"DEPOSIT.md: {path} reads {rows[path]:,} bytes, "
                       f"{ref} has {tree[path]:,}")
    total = sum(tree.values())
    m = re.search(r"\| \*\*Total\*\* \| \*\*([\d,]+)\*\*", text)
    if not m:
        out.append("DEPOSIT.md: the total row was not found")
    elif int(m.group(1).replace(",", "")) != total:
        out.append(f"DEPOSIT.md: total row reads {m.group(1)} bytes, {ref} totals {total:,}")
    m = re.search(r"\*\*(\d+) files,\s*\n?([\d,]+) bytes\*\*", text)
    if not m:
        out.append("DEPOSIT.md: the sentence above the table was not found")
    else:
        if int(m.group(1)) != len(tree):
            out.append(f"DEPOSIT.md: the sentence reads {m.group(1)} files, {ref} has {len(tree)}")
        if int(m.group(2).replace(",", "")) != total:
            out.append(f"DEPOSIT.md: the sentence reads {m.group(2)} bytes, {ref} totals {total:,}")
    if not out:
        print(f"    deposit inventory: {len(tree)} files, {total:,} bytes match {ref}")
    return out


# --- the item set's name ----------------------------------------------------------------
# S1 promised one file called `items.jsonl` while the pack holds `items.pilot.jsonl` and
# `items.real.jsonl`, each with a manifest, so the promise named a file no reader could
# find. The documents now use the pack's own per-set names, and this holds them to it: to
# each other in a clean clone, and to the files on disk where the pack is present.
PACK = ROOT / "registration-pack" / "pilot"
PACK_SETS = ("items.pilot.jsonl", "items.real.jsonl")


def check_item_set_names() -> list[str]:
    """The documents must name the same item files, and the pack must hold them.

    The item text is outside the archive by design, so a clean clone has no pack to check
    against; what it can check is that the protocol, the paper and the registration draft
    agree on the names, which is the disagreement that produced the stale promise. Where
    the pack is here, its files, their manifests and the digests those manifests record
    are held to the names the documents use, as the draft's own digest already is.
    """
    out: list[str] = []
    named: dict[str, set[str]] = {}
    for label, path in (("S1", PROTOCOL), ("paper", PAPER_MD), ("draft", DRAFT)):
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        found = set(re.findall(r"`(items\.[a-z]+\.jsonl)`", text))
        if not found:
            out.append(f"{label}: names no item-set file")
        if re.search(r"\bitems\.jsonl\b", text):
            out.append(f"{label}: names a bare `items.jsonl`, which the pack does not hold")
        named[label] = found

    reference = named.get("S1") or set(PACK_SETS)
    for label, found in named.items():
        for missing in sorted(reference - found):
            out.append(f"{label}: does not name {missing}")
        for extra in sorted(found - reference):
            out.append(f"{label}: names {extra}, which the protocol does not")

    if not PACK.exists():
        print("    (registration pack absent - item-set names compared across documents)")
        return out
    # S1 states the pilot sets' size, so the manifests are held to it rather than trusted.
    stated = re.search(r"each of (\d+) items", PROTOCOL.read_text(encoding="utf-8"))
    for name in sorted(set().union(*named.values()) if named else set(reference)):
        path = PACK / name
        if not path.exists():
            out.append(f"registration pack: {name} is named but not on disk")
            continue
        manifest = path.with_name(name.replace(".jsonl", ".manifest.json"))
        if not manifest.exists():
            out.append(f"registration pack: {name} has no manifest beside it")
            continue
        recorded = manifest.read_text(encoding="utf-8")
        m = re.search(r'"sha256": "([0-9a-f]{64})"', recorded)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if not m:
            out.append(f"registration pack: {manifest.name} records no digest")
        elif m.group(1) != digest:
            out.append(f"registration pack: {manifest.name} records {m.group(1)[:16]}..., "
                       f"{name} hashes to {digest[:16]}...")
        m = re.search(r'"bytes": (\d+)', recorded)
        size = path.stat().st_size
        if not m:
            out.append(f"registration pack: {manifest.name} records no byte count")
        elif int(m.group(1)) != size:
            out.append(f"registration pack: {manifest.name} records {m.group(1)} bytes, "
                       f"{name} is {size:,}")
        rows = sum(1 for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip())
        m = re.search(r'"records": (\d+)', recorded)
        if not m:
            out.append(f"registration pack: {manifest.name} records no item count")
        elif int(m.group(1)) != rows:
            out.append(f"registration pack: {manifest.name} records {m.group(1)} items, "
                       f"{name} has {rows}")
        elif stated is not None and int(stated.group(1)) != rows:
            out.append(f"S1: the pilot sets are stated as {stated.group(1)} items, "
                       f"{name} has {rows}")
    return out


def main() -> int:
    flags = {a for a in sys.argv[1:] if a.startswith("--")}
    if "--counts" in flags:
        for label, src, pdf in (("paper", PAPER_MD, PAPER_PDF), ("S1", PROTOCOL, S1_PDF)):
            pages = page_count(pdf)
            print(f"{label:6s} {word_count(src):,} words, "
                  f"{pages if pages is not None else '?'} pp")
        return 0
    if not PROTOCOL.exists():
        print(f"missing source: {PROTOCOL.name}")
        return 2
    text = PROTOCOL.read_text(encoding="utf-8")
    problems: list[str] = []

    try:
        table = table_rows(text)
        segments = note_segments(text)
    except (ValueError, StopIteration) as exc:
        print(f"cannot read Section 7.1: {exc}")
        return 1

    print(f"    {'row':4s} {'n':>4s} {'alpha':>10s} {'beta':>9s} {'power':>6s}")
    for row in ROWS:
        d = derived(row)
        print(f"    {row['key']:4s} {row['n']:4d} {d['alpha']:10.2e} "
              f"{d['beta']:9.2e} {d['power']:6.3f}")

        # 1. the table row
        cells = table.get(row["label"])
        if cells is None:
            problems.append(f"table: no row labelled {row['label']!r}")
        else:
            want = [str(row["n"]), f"{row['p0']:.2f}", f"{row['p1']:.2f}",
                    str(row["support"]), str(row["failure"]), f"{d['power']:.2f}"]
            got = cells[1:]
            for name, g, w in zip(("n", "p0", "p1", "support", "failure", "power"), got, want):
                same = (abs(float(g) - float(w)) <= 0.01 if name in ("p0", "p1")
                        else (abs(float(g) - float(w)) <= 0.005 if name == "power"
                              else g == w))
                if not same:
                    problems.append(f"table {row['key']}: {name} reads {g}, computes {w}")

        # 2. the note beneath it
        seg = segments.get(row["key"])
        if seg is None:
            problems.append(f"note: no entry for {row['key']!r}")
        else:
            toks = numbers(seg)
            if len(toks) < 2:
                problems.append(f"note {row['key']}: expected alpha and beta, found {len(toks)}")
            else:
                for label, (kind, value), want in (
                        ("alpha", toks[0], d["alpha"]), ("beta", toks[-1], d["beta"])):
                    if not matches(kind, want, value):
                        problems.append(
                            f"note {row['key']}: {label} reads {value:.3g}, computes {want:.3g}")

        # 3. the prediction text
        for pattern in row["text"]:
            if pattern not in text:
                problems.append(f"prediction text: expected {pattern!r}")

        # 4. the promises the section makes about itself
        if d["alpha"] > ALPHA_CEILING:
            problems.append(f"{row['key']}: alpha {d['alpha']:.3g} exceeds {ALPHA_CEILING}")
        if d["beta"] > BETA_CEILING:
            problems.append(f"{row['key']}: beta {d['beta']:.3g} exceeds {BETA_CEILING}")
        if d["band"] < MIN_BAND:
            problems.append(f"{row['key']}: band {d['band']:.3f} is under {MIN_BAND}")

    # 5. the summary sentence's two maxima
    max_alpha = max(derived(r)["alpha"] for r in ROWS)
    max_beta = max(derived(r)["beta"] for r in ROWS)
    m = re.search(r"largest\s+\$\\alpha\$\s+is\s+therefore\s+\.(\d+)", text)
    if not m or not matches("point", max_alpha, float("0." + m.group(1))):
        problems.append(f"note: largest alpha is {max_alpha:.3g}, "
                        f"the note says {m.group(0) if m else 'nothing'}")
    m = re.search(r"largest\s+\$\\beta\$\s+\.(\d+)", text)
    if not m or not matches("point", max_beta, float("0." + m.group(1))):
        problems.append(f"note: largest beta is {max_beta:.3g}, "
                        f"the note says {m.group(0) if m else 'nothing'}")

    # 6. Prediction 1's no-effect rate and the alpha it states against it. The four-way floor is
    #    not restated in P1: it is 5a's null, and a second inline value is a second thing to keep
    #    in step for no decision it changes.
    p1_line = next((ln for ln in text.splitlines() if ln.startswith("1. **Directionality.**")), "")
    if "The no-effect rate is one half" not in p1_line:
        problems.append("prediction 1: the no-effect rate is not stated as one half")
    if "two named answers" not in p1_line:
        problems.append("prediction 1: the null no longer names the two answers it contrasts")
    if "Prediction 5a" not in p1_line:
        problems.append("prediction 1: the null no longer says which prediction owns one quarter")
    inline = re.findall(r"\\alpha = ([0-9.]+) \\times 10\^\{(-?\d+)\}", p1_line)
    if len(inline) != 1:
        problems.append(f"prediction 1: expected one inline alpha, found {len(inline)}")
    elif not matches("point", derived(ROWS[0])["alpha"],
                     float(inline[0][0]) * 10 ** int(inline[0][1])):
        problems.append(f"prediction 1: inline alpha reads {inline[0][0]}e{inline[0][1]}, "
                        f"computes {derived(ROWS[0])['alpha']:.3g}")

    # 6b. the paragraph in 7.1 that explains the correction. It went unchecked until two
    #     stray control bytes passed every test, and it quotes two alphas at the same null:
    #     the old 26-of-40 line, which did not hold, and the 28-of-40 line that replaced it.
    para = next((ln for ln in text.splitlines()
                 if ln.startswith("**Prediction 1's no-effect rate was the wrong one.**")), "")
    if not para:
        problems.append("7.1: the Prediction 1 correction paragraph is missing")
    else:
        if "one half" not in para:
            problems.append("7.1: the correction paragraph no longer names the no-effect rate")
        for claim in ("26 of 40", "28 of 40"):
            if claim not in para:
                problems.append(f"7.1: the correction paragraph no longer quotes {claim}")
        quoted = []
        for m in re.finditer(r"\\alpha = ", para):
            token = TOKEN.match(para, m.end())
            if token:
                quoted.append(numbers(token.group(0))[0][1])
        if len(quoted) != 2:
            problems.append(f"7.1: expected two inline alphas in the correction paragraph, "
                            f"found {len(quoted)}")
        else:
            for got, k in zip(quoted, (26, 28)):
                want = ge(ITEMS, 0.5, k)
                if got <= 0 or abs(math.log10(want / got)) > ALPHA_QUOTE_TOLERANCE:
                    problems.append(f"7.1: the alpha for {k} of 40 reads {got:.3g}, "
                                    f"computes {want:.3g}")
        # The rate is an argument, not an assertion: the paragraph must still say why the two
        # named answers are exchangeable and why one quarter is 5a's null rather than this one.
        for anchor in ("equal footing", "Prediction 5a"):
            if anchor not in para:
                problems.append(f"7.1: the correction paragraph no longer gives {anchor!r}")

    # 6c. the paragraph that rules out the strict null, which is the other candidate rate.
    strict = next((ln for ln in text.splitlines()
                   if ln.startswith("**Why one half, and not zero.**")), "")
    if not strict:
        problems.append("7.1: the paragraph rejecting a zero no-effect rate is missing")
    else:
        for anchor in ("least favourable", "Arm B1", "proxy"):
            if anchor not in strict:
                problems.append(f"7.1: the zero-rate paragraph no longer gives {anchor!r}")

    # 7. the design facts the unit counts rest on
    for anchor in ("three replicates per item and arm-cell",
                   "120 coded chains per arm-cell and 720 in total"):
        if anchor not in text:
            problems.append(f"Section 8: expected {anchor!r}")

    problems.extend(check_multiplicity(text))
    problems.extend(check_screen(text))
    problems.extend(check_costs(text))
    problems.extend(check_no_control_characters())
    problems.extend(check_registration_draft())
    problems.extend(check_item_set_names())
    problems.extend(check_deposit_inventory())
    problems.extend(check_quotes("--skip-pages" not in flags))

    if problems:
        print(f"\n{len(problems)} disagreement(s) between the documents and their numbers:")
        for p in problems:
            print(f"  - {p}")
        return 1
    print("\nconsistent: 7.1 thresholds, 9 cost table and every quoted count")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
