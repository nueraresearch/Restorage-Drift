# Changelog

All notable changes to Restorage Drift are recorded here. The manuscript's own
version line is kept in step with the release tag, so a reader holding a PDF can
tell which release it came from.

## [1.0.0] — 2026-11-27

Initial release. Theory paper plus Supplementary Material S1. No empirical data.

### Paper

- Theory paper at 16 pp, 6,695 words, within a 7,500-word limit.
- Abstract, keywords, falsifiability conditions, open research questions,
  declarations, and 19 references.

### Attribution and scope

- Section 5.5 demotes the attractor result to a cited fixed point of iterated
  Bayesian learning (Griffiths & Kalish, 2007) instead of presenting it as a
  finding of this paper, and states the mapping explicitly: `β/(1−α)` is a
  temperature on the prior and `α` sets how many cycles of evidence survive.
- The claim is re-pointed at the surviving support: the limit is the prior
  restricted to the candidates that remain, so systems matched on prior and
  parameters diverge if their compressions removed different candidates.
- Section 5 separates gradual probability drift, direct representational loss,
  and delayed evidence-mediated loss, with *T*<sub>A</sub> distinguished from
  *T*<sub>d</sub> and *T*<sub>o</sub> (see the model replacement note below).
- Kirby, Dowman & Griffiths (2007) cited in Sections 4 and 5.5 for
  bottleneck-governed departure from unbiased copying; their MAP result is
  described as magnification of the prior's ordering, not as a power law.
- Sections 4 and 7 split the inherited result from the paper's own claim, so
  neither implies the convergence theorem is new.
- Abstract no longer presents convergence-on-the-prior as the framework's
  finding, and no longer describes the test as already pre-registered.

### Citations added before release

- Section 4 cites the iterated-learning treatment of model collapse directly
  (Ren et al., 2024; Guo et al., 2026) and the compression–communication
  tradeoff (Kirby et al., 2015), which was the result the model-collapse bullet
  had been relying on without naming. The bullet now separates this framework
  from that account on two points rather than by assertion: there the hypothesis
  space is fixed in advance by a frozen base model and every cycle carries a
  learning step, whereas here the retained set is produced by the trajectory and
  re-storage alone closes the loop.
- Section 7 records that the filter contrast in Guo et al. (2026) — uninformed
  filtering indistinguishable from no filter, quality-grounded filtering
  sustaining structure — is the artificial form of the paper's own prediction
  that only a check which restores state can move *T*<sub>d</sub> outward.
- The Bayesian and predictive-frameworks bullet in Section 4, which previously
  made a literature claim with no citation, now cites Clark (2013).

### Model replaced before release

- Section 5 was replaced with a model that separates three objects the previous
  version conflated: the candidate space *K*ₙ, the evidence state *E*ₙ(*x*), and
  the reconstructed distribution *S*ₙ. Section 5.8 states the reason: with fixed
  *k*, positive retained weights and a positive prior, top-*k* truncation selects
  a support once at the first compression and then does nothing, because
  reconstruction only reweights within the set it has already chosen. The
  previous version's central claim — endogenous, trajectory-dependent support
  truncation — therefore described a mechanism that fires once, and the two
  regimes built on it were not as distinct as claimed.
- The replacement models irreversible candidate removal and evidence decay below
  an availability threshold as separate pathways, and proves three conditional
  results: nested active support, finite support stabilization, and convergence
  to a power-weighted prior restricted to the surviving set.
- Drift is now three outcomes rather than two — gradual probability drift, direct
  representational loss, and delayed evidence-mediated loss — with *T*<sub>A</sub>
  (availability) separated from *T*<sub>d</sub> (majority) and *T*<sub>o</sub>
  (overtaking).
- The resource budget is demoted to a hypothesis throughout: the claim that
  total compression entails total prior capture, and the *W* → 0 limit that
  carried it, are removed rather than restated.
- The one-half threshold is no longer described as measuring how much of a
  reconstruction the prior supplied; it is a majority-loss convention.
- The Griffiths & Kalish (2007) attribution is retained in Section 5.5 and is
  stronger for the new model, since convergence is now proved locally and then
  attributed rather than asserted by analogy.

### Figures

- Figure 2's caption states that *k* = 4 against a four-candidate item, so
  candidate restriction is inactive: the figure isolates prior-weighted
  reweighting on a fixed support and is used to illustrate Proposition 3 and the
  separation of *T*<sub>d</sub> from *T*<sub>o</sub>. It carries no claim about
  dynamic candidate loss, and its budget labels are described as illustrative
  parameter settings rather than as a derived resource law.

### Supplementary

- S1: pre-registration-ready test protocol — five arms, nine predictions
  specified in advance, analysis plan, cost envelope. Two measures were added so
  that the protocol tests the mechanisms the theory separates rather than only
  the reweighting: an availability landmark *T*<sub>A</sub> estimated from
  recovery under a fixed probe procedure, and a blinded four-point evidence
  score for *E*<sub>n</sub>(*x*) coded from the stored text independently of
  response frequency. Both carry their own predictions, and the coding cost is
  stated as person-hours because it, not the API bill, limits the measure. Registration fields drafted while preparing the protocol are held outside the archived record as unreleased working material, so the released protocol carries no thresholds that have not been justified.
- S2 (`Human Restorage Study`, v1.2) is held outside the archived record: not
  cited by the paper and not part of this release package. Its version number
  is deliberately not reset to 1.0. Its header states the same, so the PDF cannot be read as a supplement, and it no longer labels itself Supplementary Material S2.

### Known open items at release

- OSF registration of S1 not yet created. The paper describes S1 as prepared
  for pre-registration, not as registered.
- Preprint not yet posted; no DOI yet. The README citation will be updated when
  one exists.

### Corrections after first publication (27 November 2026, before deposit)

Five corrections were made to the tagged text after v1.0.0 was first published, and
before the release was deposited, together with two fixes to the build scripts:

- Abstract: the three drift outcomes were said to share an endpoint. Proposition 3
  takes its limit over the surviving set, so gradual drift leaves mass on the original
  while both loss pathways leave none. The abstract now reads as a prior-dominated
  terminus that differs in which candidates survive, which a terminal measurement
  alone need not distinguish.
- README: the same claim in the repository summary, corrected the same way.
- S1, Arm B2: the passage said a reappearance of a dropped candidate "is prior
  reconstruction". It now states only the absorbing-support consequence: the
  candidate leaves the active set and cannot return through reconstruction.
- S1, evidence landmark: the landmark was defined on the lower of the two codings
  while the rule required both coders to score below "compatible". It now takes the
  higher, so it fires only on coder agreement.
- S1, Prediction 4: "pure prior reconstruction" became reconstruction of the prior
  over the survivors.
- Build scripts: `make_docx.py` named a working document that is not in the release, so
  `python make_docx.py` failed with `missing source` on a fresh clone; its default list
  now covers the two released documents, and any other is built by passing its name.
  `figures/make_figures.py` hardcoded a MiKTeX directory under the author's user profile
  as a fallback for when `kpsewhich` was unavailable; that path is gone, and the faces
  resolve through `kpsewhich` or an `LM_FONT_DIR` override, failing with the names of the
  missing files. The figures regenerate byte-identically, so no artwork changed.

One item left the release notes rather than being corrected. The bullet recording that
Figure 1 had not been checked at print resolution described an earlier state of the
work, not the state of the release: the figure was rendered and inspected at print
resolution before deposit, and no change to the artwork followed. Removing the bullet
changes only this record, not the paper, the figures or the build.

The paper is 6,695 words (was 6,692) and S1 3,162 (was 3,142); both PDFs and DOCX
builds were regenerated, and the word count was updated wherever it was quoted. Page
counts are unchanged at 16 and 6.
