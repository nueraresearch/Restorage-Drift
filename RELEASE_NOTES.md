# Restorage Drift v1.0.0

Theory paper and its companion test protocol. No empirical data.

## Contents

- `Restorage Drift.pdf` — the theory paper, 16 pp, 6,729 words.
- `Iterative-Summarization Protocol.pdf` — Supplementary Material S1, the test protocol, 7 pp.
- Markdown sources, `.docx` builds, both figures, and the scripts that produce all of it.

## Figures

Both figures are set entirely in Latin Modern — labels, glosses, tick labels, legend and the β in Figure 2's parameter key — the same faces as the manuscript, so no figure introduces a second typeface. `figures/make_figures.py` finds those fonts through `kpsewhich`; it holds no hard-coded system font path.

## Build

Both PDFs rebuild byte-for-byte from a clean clone of the tag: `build.py` pins the timestamp pdfTeX writes and replaces each trailer `/ID` with a digest of the file.

## What is claimed

Section 5 separates three things that a single measure conflates: which candidates a system can still represent, how much evidence survives for each, and how much reconstructed probability each receives. Two compression pathways are modelled apart — irreversible candidate removal and evidence decay below an availability threshold — and the model yields three conditional results: nested active support, finite support stabilization, and convergence of the reconstruction to a power-weighted prior restricted to the survivors. Section 5.5 attributes that convergence to Griffiths & Kalish (2007) and claims only the restriction of the limit to the surviving support, which is what makes the attractor depend on which candidates survived. Drift is three outcomes rather than two: gradual probability drift, direct representational loss, and delayed evidence-mediated loss. Section 5.8 records why the fixed-*k* truncation used in earlier drafts cannot produce the latter two: with positive retained weights it selects a support once and then does nothing.

## What is not claimed

No empirical data, in this or any domain. No validation of the framework in human memory, organizations, cultural transmission, or AI systems — cross-system application is stated as a hypothesis throughout. No study has been run, and no registration exists; the protocol is described as prepared for pre-registration, which is what it is.

## Not part of this release

`Human Restorage Study.*` — working design document, v1.2 — and `Registration Fields Draft.md` — unreleased draft of OSF preregistration fields. Both are withheld from the archived tree, so neither is part of the DOI record; they remain local working files, untracked and untagged. Neither is cited by the paper, and the draft's bracketed thresholds have not been justified.

## Licence

Text and figures: CC BY 4.0. Build scripts: MIT. See `LICENSE`.
