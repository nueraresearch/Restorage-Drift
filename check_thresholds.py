#!/usr/bin/env python3
"""Check the protocol's derived numbers against the arithmetic that produces them.

Two blocks qualify. Section 7.1 states a count and two error rates per prediction, in a
table, a note and nine predictions that have to agree. Section 9 states call counts,
token estimates and band-share sensitivities that are all products of the design. Both
have drifted before, so build.py runs this first and refuses to make a PDF if it fails.

    python check_thresholds.py      # exit 0 when consistent, 1 with a report

ROWS is the specification for 7.1: unit count, the no-effect rate, the minimum effect,
and the two lines. alpha, beta and power are recomputed here from those four, so a
number written into the document cannot drift from the arithmetic behind it. The cost
constants below play the same role for 9, and the prose that states them is anchored
too, so changing a replicate count in one place and not the other fails the check.
"""
from __future__ import annotations

import math
import re
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

ROWS = [
    {"key": "1", "label": "1 Directionality", "n": ITEMS, "p0": 0.25, "p1": 0.75,
     "support": 26, "failure": 22,
     "text": ["at least 26 of 40 items", "at most 22 of 40"]},
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
MIN_BAND = 0.04          # the note promises a band of at least 4% of the units
LOG_TOLERANCE = 0.05     # ~12% in ratio terms, for values quoted to two figures

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


def main() -> int:
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

    # 6. the bound Prediction 1 states inline
    if r"\alpha < 10^{-6}" in text and not derived(ROWS[0])["alpha"] < 1e-6:
        problems.append("prediction 1: the inline alpha bound does not hold")

    # 7. the design facts the unit counts rest on
    for anchor in ("three replicates per item and arm-cell",
                   "120 coded chains per arm-cell and 720 in total"):
        if anchor not in text:
            problems.append(f"Section 8: expected {anchor!r}")

    problems.extend(check_costs(text))

    if problems:
        print(f"\n{len(problems)} disagreement(s) between the protocol and its arithmetic:")
        for p in problems:
            print(f"  - {p}")
        return 1
    print("\nconsistent: 7.1 table, note and predictions agree; 9 cost table recomputes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
