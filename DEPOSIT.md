# Deposit record

What was checked before this release could be deposited, how, and what a reviewer can
re-run. Every figure names the tree it belongs to, so it can be checked against Git
rather than against a page that may have been cached.

## The source archive

Zenodo archives a release's Git tree: the tracked files at the tag, without `.git` and
without anything untracked or ignored. This release's tree is **21 files,
1,822,138 bytes**:

| File | Bytes |
| :---- | ----: |
| `.gitattributes` | 114 |
| `.gitignore` | 455 |
| `.zenodo.json` | 2,222 |
| `CHANGELOG.md` | 36,552 |
| `DEPOSIT.md` | 6,295 |
| `Iterative-Summarization Protocol.docx` | 30,822 |
| `Iterative-Summarization Protocol.md` | 41,385 |
| `Iterative-Summarization Protocol.pdf` | 270,337 |
| `LICENSE` | 3,009 |
| `README.md` | 6,453 |
| `RELEASE_NOTES.md` | 3,132 |
| `Restorage Drift.docx` | 321,217 |
| `Restorage Drift.md` | 50,068 |
| `Restorage Drift.pdf` | 664,459 |
| `build.py` | 10,922 |
| `check_thresholds.py` | 49,371 |
| `fig-header.tex` | 200 |
| `figures/fig1-cycle.png` | 115,158 |
| `figures/fig2-drift.png` | 189,954 |
| `figures/make_figures.py` | 12,184 |
| `make_docx.py` | 7,829 |
| **Total** | **1,822,138** |

Reproduce the count and the total:

```sh
git ls-tree -r --long v1.0.0 | awk '{n++; s+=$4} END {print n, s}'
```

The row for `DEPOSIT.md` is this file's own size in the tree, so the table and the total
include the page that reports them. Line endings are fixed by `.gitattributes`, so the
bytes an archive holds are the bytes a checkout holds; a working copy converted to CRLF
would print more and is not what Zenodo receives.

## What is not in it, and how that was shown

Three groups must stay out of the public record: the human-study design (`Human Restorage
Study.md`, `.pdf`, `.docx`), the preregistration draft (`Registration Fields Draft.md`), and
build intermediates (`*.aux`, `*.log`, `*.out`, `*.toc`, `*.synctex.gz`, `*.pyc`,
`__pycache__/`, `.tmp_*`).

The exclusion was checked against the Git index, not against the ignore rules. A
`.gitignore` entry says nothing about whether a file was committed before the rule was
added, so it cannot certify absence; these commands can:

```sh
git ls-tree -r --name-only v1.0.0 | grep -icE 'study\.(md|pdf|docx)|registration fields'
git ls-tree -r --name-only v1.0.0 | grep -icE '\.(aux|log|out|toc|synctex\.gz|pyc)$|__pycache__|\.tmp_'
git ls-files --others --exclude-standard
```

At the time of the check the first two printed `0` and the third printed nothing: no file
from those groups was tracked, and no untracked file existed that a later commit could have
carried in.

## The registration, and what ties it to this deposit

`Registration Fields Draft.md` is the file that would be pasted into an OSF pre-registration,
and it is the one document this record deliberately does not contain. It is held outside the
archive and outside this repository — untracked, untagged, excluded by `.gitignore` — so a
reader cannot obtain it from the DOI. What this record can do is name it by content, so that
"the registered text" is a byte sequence rather than a description of one:

| | |
| :---- | :---- |
| File | `Registration Fields Draft.md` |
| SHA-256 | `73430eeb0fecda94428adb63463cbf3d5df5267f5bbd427e7c65176ed5b6ba54` |
| Bytes | 10,809 |
| Lines | 43 |
| Measured at | tag `v1.0.0`, before the deposit |

Reproduce it on a machine that holds the file:

```sh
sha256sum "Registration Fields Draft.md"   # 73430eeb...
wc -c < "Registration Fields Draft.md"      # 10809
```

Those two values identify the text that matches S1 v1.0.0 — its per-row $\alpha \le .01$,
its family of four hypotheses with Holm steps .0125 to .05, its four-item slice and its
40-item run, and its contamination threshold of 9 of 20 at $p = .041$. A copy with a
different digest is a different registration, whatever its filename, and the deposit cannot
say which one was registered: the archive holds no copy to compare against. The digest is
therefore checked where it can be — the build's draft guard hashes the file, compares it
with this table, and fails when either value disagrees — and is a claim about a file the
reader must obtain from the author when the file is absent.

## The metadata, and which schema settled it

Two schemas disagree about `.zenodo.json`, and the disagreement is why this section exists.

- **Zenodo's frozen legacy JSON schema** (`zenodo/modules/deposit/jsonschemas/deposits/records/legacyrecord.json`,
  `additionalProperties: false`) reports exactly one problem: `version` and `language` are
  not among its allowed properties. That schema belongs to the pre-2023 Zenodo, retired when
  the service moved to InvenioRDM.
- **The maintained schema for the current API** (zenodraft `metadata-schema-zenodo`,
  draft-07) validates the file with **0 errors**: `license: CC-BY-4.0` is in its 512-entry
  licence enumeration, `version` and `language` are permitted, and `"eng"` satisfies its
  language pattern `^[a-z]{2,3}$`.

The live software sides with the second. `.zenodo.json` is read by
`site/zenodo_rdm/legacy/deserializers/metadata.py`, which declares
`version = SanitizedUnicode()` and `language = fields.Method(deserialize="load_language")`
and maps `language` onto `languages`; Zenodo's own `.zenodo.json` documentation shows both
fields in its example. The strict legacy schema is therefore not the test a deposit is put
to, and `build.py` does not reproduce it. `check_metadata()` there enforces the fields the
deposit requires and fails the build when one is missing or malformed, so the claims in
this section are re-checked on every build rather than resting on a transcript.

## What this record does not establish

- No deposit has been made and no DOI exists. A DOI is minted when the GitHub release is
  created and the Zenodo record is published; until then the citation in `README.md` points
  at the repository and its tag.
- The metadata check is static. It shows the file carries the required fields; it does not
  show that Zenodo's servers accept the deposit. Only a sandbox deposit does that.
- An archive hash quoted from a dry-run transcript is not the hash GitHub serves, since it
  depends on the archive prefix and file timestamps. Compare the file list and the total.
