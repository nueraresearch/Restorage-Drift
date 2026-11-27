# Deposit record

What was checked before this release could be deposited, how, and what a reviewer can
re-run. Every figure names the commit it belongs to, so it can be checked against Git
rather than against a page that may have been cached.

## The source archive

Zenodo archives a release's Git tree: the tracked files at the tag, without `.git` and
without anything untracked or ignored. The dry run measured that tree at `a4f130d`, where
it held **20 files, 1,719,125 bytes**:

| File | Bytes |
| :---- | ----: |
| `.gitattributes` | 114 |
| `.gitignore` | 455 |
| `.zenodo.json` | 1,881 |
| `CHANGELOG.md` | 21,036 |
| `Iterative-Summarization Protocol.docx` | 25,829 |
| `Iterative-Summarization Protocol.md` | 33,868 |
| `Iterative-Summarization Protocol.pdf` | 260,670 |
| `LICENSE` | 2,611 |
| `README.md` | 6,101 |
| `RELEASE_NOTES.md` | 2,797 |
| `Restorage Drift.docx` | 320,655 |
| `Restorage Drift.md` | 49,551 |
| `Restorage Drift.pdf` | 641,138 |
| `build.py` | 4,923 |
| `check_thresholds.py` | 22,171 |
| `fig-header.tex` | 200 |
| `figures/fig1-cycle.png` | 115,158 |
| `figures/fig2-drift.png` | 189,954 |
| `figures/make_figures.py` | 12,184 |
| `make_docx.py` | 7,829 |
| **Total** | **1,719,125** |

Reproduce the count and the total:

```sh
git ls-tree -r --long a4f130d | awk '{n++; s+=$4} END {print n, s}'
```

That command needs the commit object, so run it in a full clone, or `git fetch origin
a4f130d` first: a shallow clone carries only the tag's tip.

Two later commits moved the total without changing the file list: `LICENSE` was rewritten
for the single-licence framing and `build.py` gained the metadata check. At `4164565` the
same 20 files total 1,725,436 bytes. This record is one further file, so the tag that
contains it holds 21; `git ls-tree -r --long v1.0.0` prints that total, and the table above
is the measurement the dry run reported.

## What is not in it, and how that was shown

Three groups must stay out of the public record: the human-study design (`Human Restorage
Study.md`, `.pdf`, `.docx`), the preregistration draft (`Registration Fields Draft.md`), and
build intermediates (`*.aux`, `*.log`, `*.out`, `*.toc`, `*.synctex.gz`, `*.pyc`,
`__pycache__/`, `.tmp_*`).

The exclusion was checked against the Git index, not against the ignore rules. A
`.gitignore` entry says nothing about whether a file was committed before the rule was
added, so it cannot certify absence; these commands can:

```sh
git ls-tree -r --name-only a4f130d | grep -icE 'study\.(md|pdf|docx)|registration fields'
git ls-tree -r --name-only a4f130d | grep -icE '\.(aux|log|out|toc|synctex\.gz|pyc)$|__pycache__|\.tmp_'
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
| SHA-256 | `313091d29dff04b1a0e166783ba330445a72aa4666f6852302ef01e3a91e4c50` |
| Bytes | 10,684 |
| Lines | 43 |
| Measured at | tag `v1.0.0`, before the deposit |

Reproduce it on a machine that holds the file:

```sh
sha256sum "Registration Fields Draft.md"   # 313091d2...
wc -c < "Registration Fields Draft.md"      # 10684
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
