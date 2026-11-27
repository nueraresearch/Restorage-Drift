#!/usr/bin/env python3
"""Break each guard in turn and confirm the checker catches it.

    python tests/mutation_check.py            # every mutation, restore after each
    python tests/mutation_check.py -k alpha   # only the ones whose name contains "alpha"

A guard that passes its own test is still unguarded: an edit can silence one by rewording an
anchor, and the release then ships with a claim nothing verifies. This script is the other
half of `check_thresholds.py` - every check it names is broken here on purpose, and a
mutation that the checker fails to notice is reported as a miss.

Each mutation edits one tracked file, runs the checker, and restores the file from the bytes
it read, so a run leaves the tree exactly as it found it; the script verifies that at the end
and exits non-zero if anything was left changed. Guards that depend on working material held
outside the archive - the registration draft and the item-set pack - are skipped, with a note,
on a machine that does not have them, exactly as the checker itself skips those checks.
"""
from __future__ import annotations

import hashlib
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
S1 = ROOT / "Iterative-Summarization Protocol.md"
DEPOSIT = ROOT / "DEPOSIT.md"
DRAFT = ROOT / "Registration Fields Draft.md"
MANIFEST = ROOT / "registration-pack" / "pilot" / "items.real.manifest.json"
CHECKER = ROOT / "check_thresholds.py"


def run_checker() -> tuple[int, str]:
    proc = subprocess.run([sys.executable, str(CHECKER), "--skip-pages"], cwd=ROOT,
                          capture_output=True, text=True, encoding="utf-8",
                          env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    return proc.returncode, proc.stdout + proc.stderr


def tracked_files() -> list[Path]:
    listing = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True)
    if listing.returncode != 0:
        return []
    return [ROOT / name for name in listing.stdout.splitlines() if name.strip()]


def digest_tree() -> dict[str, str]:
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in tracked_files() if p.exists()}


def apply(path: Path, old: str, new: str) -> bool:
    text = path.read_bytes().decode("utf-8")
    if old not in text:
        return False
    path.write_text(text.replace(old, new, 1), encoding="utf-8", newline="\n")
    return True


def digest_mutation() -> tuple[str, str] | None:
    """The digest prefix the reproduce block prints, and a same-length wrong one.

    Read from DEPOSIT.md rather than written here: the draft is re-hashed whenever it is
    edited, and a hard-coded prefix turns this mutation into a silent skip exactly when the
    guard it tests is most likely to be needed.
    """
    m = re.search(r"# ([0-9a-f]{8})\.\.\.", DEPOSIT.read_text(encoding="utf-8"))
    if not m:
        return None
    prefix = m.group(1)
    flipped = ("0" if prefix[0] != "0" else "1") + prefix[1:]
    return f"# {prefix}...", f"# {flipped}..."


def inventory_row() -> tuple[str, str] | None:
    """A DEPOSIT inventory row whose size can be nudged without changing the file's length."""
    text = DEPOSIT.read_text(encoding="utf-8")
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("| `") or stripped.count("|") != 3:
            continue
        name = stripped.split("`")[1]
        size = stripped.split("|")[2].strip()
        if name in ("DEPOSIT.md",) or not size.replace(",", "").isdigit():
            continue
        bumped = f"{int(size.replace(',', '')) + 1:,}"
        if len(bumped) == len(size):
            return size, bumped
    return None


def mutations() -> list[tuple[str, Path, str, str, str]]:
    """(title, file, old, new, the text the checker must print)."""
    out = [
        ("S1 control byte", S1, "\\alpha", "\x07alpha", "control byte"),
        ("7.1 alpha quote", S1, r"at $\alpha = .040$", r"at $\alpha = .052$",
         "alpha for 26 of 40"),
        ("P1 loses its contrast", S1, "two named answers", "two answers",
         "names the two answers"),
        ("7.1 loses the argument", S1, "equal footing", "equal terms", "equal footing"),
        ("7.1 zero-rate paragraph", S1, "**Why one half, and not zero.**", "**Why one half.**",
         "zero no-effect rate is missing"),
        ("item-level rule loses its replicate count", S1,
         "mean of its ten chains' terminal distributions",
         "mean of its chains' terminal distributions",
         "item-level rule for the modal answer"),
        ("tie rule removed", S1, "tie for the largest share", "tie for the largest count",
         "tie rule"),
    ]
    row = inventory_row()
    if row is not None:
        out.append(("DEPOSIT inventory row", DEPOSIT, f"| {row[0]} |", f"| {row[1]} |",
                    "DEPOSIT.md:"))
    digest = digest_mutation()
    if digest is not None:
        out.append(("DEPOSIT reproduce digest", DEPOSIT, digest[0], digest[1],
                    "reproduce block prints"))
    if DRAFT.exists():
        out.append(("draft names a bare items.jsonl", DRAFT, "**Item set.**",
                    "**Item set.** `items.jsonl`.", "names a bare"))
    if MANIFEST.exists():
        out.append(("item-set manifest digest", MANIFEST, '"sha256": "8', '"sha256": "7',
                    "registration pack"))
    return out


def main() -> int:
    only = None
    if "-k" in sys.argv:
        i = sys.argv.index("-k")
        if i + 1 < len(sys.argv):
            only = sys.argv[i + 1]

    before = digest_tree()
    baseline_rc, baseline_out = run_checker()
    if baseline_rc != 0:
        print("baseline: the checker already fails, so a mutation proves nothing")
        print("\n".join(ln for ln in baseline_out.splitlines() if ln.startswith("  - ")))
        return 2
    print("baseline: checker exits 0")

    caught = missed = skipped = 0
    for title, path, old, new, expect in mutations():
        if only and only not in title:
            continue
        if not path.exists():
            print(f"  {title}: skipped (file absent)")
            skipped += 1
            continue
        backup = path.read_bytes()
        if not apply(path, old, new):
            print(f"  {title}: SKIPPED - {old!r} not found")
            skipped += 1
            continue
        try:
            rc, out = run_checker()
        finally:
            path.write_bytes(backup)
        hit = [ln.strip() for ln in out.splitlines() if expect in ln]
        if rc != 0 and hit:
            print(f"  {title}: caught")
            caught += 1
        else:
            print(f"  {title}: MISSED - the checker accepted it")
            missed += 1

    after = digest_tree()
    changed = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
    if changed:
        print(f"tree not restored: {', '.join(changed)}")
        return 2
    rc, out = run_checker()
    print(f"restored: {caught} caught, {missed} missed, {skipped} skipped; "
          f"checker exit {rc} after restore")
    return 0 if missed == 0 and rc == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
