# Restorage Drift

**A theory of information state evolution under repeated compression and reconstruction.**

J.B.T. Beebe · ORCID [0009-0009-2394-9714](https://orcid.org/0009-0009-2394-9714)

Version 1.0.0 — 27 November 2026. Preprint; not peer reviewed.

## What this is

Restorage Drift is a proposed theoretical framework, not an established scientific result. It advances the hypothesis that repeated cycles of compression, reconstruction, and re-storage produce structured information-state evolution under resource constraints, including threshold transitions and attractor convergence.

**No empirical data are reported in this release.** Cross-system application — to human memory, organizations, cultural transmission, or artificial systems — remains a hypothesis requiring independent empirical investigation. Nothing in this repository is evidence for the framework.

## What is claimed as new

Convergence of iterated transmission on a learner's prior is not new: Griffiths and Kalish (2007) established it for iterated Bayesian learning, and Kirby, Dowman and Griffiths (2007) showed that the transmission bottleneck, rather than prior strength, governs how far the outcome departs from unbiased copying.

What this paper claims is narrower. It separates three things that a single measure confounds: which candidates a system can still represent, how much evidence survives for each, and how much reconstructed probability each receives. Two compression pathways are modelled apart — irreversible removal of candidates and decay of evidence below an availability threshold — and only the third operation is reconstruction. Under stated conditions the active candidate set is nested and eventually stabilizes; once it does, the reconstructed distribution converges to a power-weighted prior restricted to the survivors. Two systems with the same prior and parameters therefore reach different attractors if their compressions removed different candidates. The model yields three distinguishable outcomes — gradual probability drift, direct representational loss, and delayed evidence-mediated loss — which share an endpoint and which terminal measurement cannot tell apart. Section 5.8 records why the fixed-*k* truncation used in earlier drafts cannot produce the second or third: with positive retained weights it selects a support once and then does nothing.

## Contents

| File | What it is |
|---|---|
| `Restorage Drift.md` `.pdf` `.docx` | The theory paper, 16 pp, 6,692 words |
| `Iterative-Summarization Protocol.md` `.pdf` `.docx` | Supplementary Material S1: the pre-registration-ready test protocol |
| `build.py` | Rebuilds the paper and S1 PDFs |
| `make_docx.py` | Rebuilds the `.docx` files with fixed table geometry |
| `fig-header.tex` | LaTeX header shared by both PDF builds |
| `figures/fig1-cycle.png` | Figure 1: the operational cycle, with re-storage highlighted |
| `figures/fig2-drift.png` | Figure 2: prior-weighted reweighting on a fixed support, at two reconstruction settings |
| `figures/make_figures.py` | Draws both figures, at the parameters stated in the paper |

## Held outside this record

Two working documents are not in this repository and not in the archived release, so the DOI covers neither:

- `Human Restorage Study.*` — human-study design, v1.2. Uncited by the paper; its own header says it is not a supplement.
- `Registration Fields Draft.md` — draft OSF preregistration fields extracted from S1. Its bracketed thresholds have not been justified; do not register as-is.

## Build

Requires Pandoc and a LaTeX distribution providing `pdflatex`.

```
python build.py
```

That rebuilds `Restorage Drift.pdf` and `Iterative-Summarization Protocol.pdf`. A single file by hand:

```
pandoc "Restorage Drift.md" -o "Restorage Drift.pdf" \
  --pdf-engine=pdflatex --pdf-engine-opt=-interaction=nonstopmode \
  --pdf-engine-opt=-halt-on-error --include-in-header fig-header.tex \
  -V geometry:margin=1in -V fontsize=11pt
```

Word count, measured with the LaTeX layout blocks stripped:

```
sed -e '/```{=latex}/,/```/d' "Restorage Drift.md" | wc -w
```

Current count: 6,692 words, against a 7,500-word journal limit.

## How the framework could fail

Section 7 of the paper lists four conditions that would undermine it: no measurable drift under strict resource constraints; drift that is white-noise divergence with no relation to priors; no convergence or threshold behaviour across compression modes; and chains sharing a prior that converge on different attractors.

S1 specifies the test. Two of its arms are controls the framework cannot survive without — verbatim transport (compression is not the mechanism) and star topology (re-storage is not the mechanism) — and a third separates instant from gradual drift.

## Citation

Cite the archived version, not this repository. A DOI will be added here when the preprint is posted; until then, cite as:

> Beebe, J.B.T. (2026). *Restorage Drift: A Theory of Information State Evolution Under Repeated Compression and Reconstruction* (Version 1.0.0) [Preprint].

## Licence

Text and figures: CC BY 4.0. Build scripts: MIT. See `LICENSE`.
