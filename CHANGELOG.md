# Changelog

All notable changes to Restorage Drift are recorded here. The manuscript's own
version line is kept in step with the release tag, so a reader holding a PDF can
tell which release it came from.

## [1.0.0] — 2026-11-27

Initial release. Theory paper plus Supplementary Material S1. No empirical data.

### Paper

- Theory paper at 16 pp, 6,729 words, within a 7,500-word limit.
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

The build is now reproducible. `build.py` pins `SOURCE_DATE_EPOCH` for the PDF step and
replaces each trailer `/ID` with a digest of the finished file; `make_docx.py` pins the
W3CDTF dates in `docProps/core.xml` and the timestamp on every zip entry. A clean clone
of the tag therefore rebuilds both PDFs and both DOCX companions byte-for-byte. All four
files were regenerated for this reason: their content is unchanged — identical extracted
text, identical `document.xml`, same page and table counts — and the only bytes that
differ from the first published files are the embedded dates, the `/ID` and the zip
timestamps.

That pass left the paper at 6,695 words (was 6,692) and S1 at 3,162 (was 3,142); both
PDFs and DOCX builds were regenerated, and the word count was updated wherever it was
quoted. Page counts were unchanged at 16 and 6.

### Second correction pass (27 November 2026, before deposit)

Four corrections from an external review, all of them in the released text:

- S1, Prediction 4: the arm B2 prediction said the later cycles "reconstruct the prior
  over the survivors". B2 copies the retained span character for character and never
  re-inserts the dropped candidate, so there is no reconstruction for that clause to
  describe. The prediction now says that any mass at the dropped candidate in a later
  measurement comes from the probe generating it out of the model's prior, not from the
  stored state, which is what the arm can actually show.
- S1, Section 9: the full-run coding estimate counted stored texts rather than codings.
  Two coders over 7,200 subsampled texts is 14,400 codings, so the full run is about 240
  person-hours, not 120. The minimal-slice figure already doubled for the second coder
  and was correct.
- Paper, Section 1: the attractor was defined as a "self-reinforcing" state configuration
  that "resist[s] further departure". Proposition 3 proves something narrower: convergence
  of the reconstructed distribution once the active support has stabilized, with the limit
  fixed by the prior restricted to the survivors. The definition now states that limit and
  says an attractor is a distribution over candidates, not a single state. The entry is
  renamed from "Attractor State" to "Attractor" so the label stops contradicting it.
- README: S1 is described as a proposed validation protocol rather than a
  pre-registration-ready one, since its decision rules are still directional.

That pass left the paper at 6,729 words (was 6,695) and S1 at 3,207 (was 3,162); both
PDFs and both DOCX builds were rebuilt and every quoted count updated. Page counts were
16 and 6.

### Registration pass (27 November 2026, before deposit)

S1 was directional where a registration needs numbers, and its probe budget priced the
base sampling rate rather than the adaptive rule. Both are now fixed.

- Section 7: all nine predictions carry a numeric criterion. Directionality is 30 of 40
  items with a failure line of 20; the survival claims are decided by hazard ratios with
  95% intervals excluding 1; re-storage additionally requires at least 20% of Arm C
  chains censored; compression necessity sets 95%, 10% and 90% tolerances across the
  three B conditions; the Arm D pair criterion is 75% of pairs ordered and a
  total-variation distance of 0.20 to the prior; mode sensitivity is two cycles in 60%
  of items; the availability-order check tolerates 2% violations as coding noise and
  otherwise reports a pipeline fault.
- Section 7 also states how a result becomes a verdict: support, failure, or
  indeterminate, with the count of indeterminate verdicts reported; intervals for every
  estimate; no family-wise adjustment across nine distinct claims; and any Krippendorff
  alpha below .80 voiding the evidence-based predictions before outcome is examined.
- Section 9 now prices the adaptive probe rule at 28 samples per measurement, the
  expectation at 20% of measurements in the [0.35, 0.65] band. Probe calls rise from
  48,000 and 480,000 to 67,200 and 672,000; totals to 69,600 and 696,000; tokens to about
  7.0M and 70M. The 10% and 30% band shares and the 60-draw ceiling are given so the
  planning figure is revised from the minimal slice instead of assumed twice.
- Section 9 also records that the minimal slice is not scored against these thresholds,
  since a 75% criterion over four items is three items, and that the 40-item run is what
  they are set for.

S1 is now 7 pp, 3,943 words (was 6 pp, 3,207). The paper is unchanged at 16 pp, 6,729
words.

### Threshold calibration pass (27 November 2026, before deposit)

Two numerical problems, both in S1, both visible only by reading Section 5.5 of the
theory against Section 7 of the protocol.

- The failure line for Prediction 1 sat at 20 of 40, which was the no-effect rate while
  one half was taken as chance. It fired on 56% of runs in which nothing was happening
  and on none of the runs the study is powered for: a verdict that cannot distinguish
  the null from the alternative. Every count-based line is now derived from exact
  binomial error rates against a stated no-effect rate, with support at alpha <= .01,
  failure at beta <= .10, and power reported. Prediction 1 becomes 26 of 40 against
  22 of 40 (alpha 1e-7, beta .005, power .95 at a .75 effect). Prediction 7 becomes 28
  of 40 against 23 of 40, its no-effect rate being one half (alpha .008, power .96 at
  .80). Prediction 9 becomes 90 of 120 against 84 of 120 (power .93). Prediction 5,
  which has only 20 pairs to work with, becomes 14 of 20 against 9 of 20 (power .79),
  and the table names it as the least powered claim.
- Prediction 9's chain count was wrong in that table. Section 8 codes three replicates
  per item and cell, so Arm A at W = 15 yields 120 coded chains rather than the 400 the
  arm runs, and a support line at 280 of 400 could not be reached by any outcome of the
  coded subsample. The line is re-derived at 120 by the same method, Section 7.1 states
  the coded count beside the row, and Section 8 states the subsample size: 120 chains
  per arm-cell, 720 in total. The table also lost its two error-rate columns, which
  hyphenated every row label at the page width; the bounds they carried are now stated
  in the sentence beneath it.
- Prediction 5 required terminals within total-variation distance 0.20 of the prior.
  Proposition 3's limit is the tempered prior, and at the theory's own illustrative
  settings that distance is 0.29, so the criterion was unsatisfiable by construction.
  S1 now tests mode agreement, which monotone tempering preserves, and reports distance
  against the implied exponent instead of scoring it. The theory states the same
  distinction in Section 5.5, with the 0.07 and 0.29 values.
- New Section 7.1 gives the derivation, the per-prediction table, a 200,000-run Monte
  Carlo check of the Prediction 1 rule, and the line between inferential thresholds and
  the tolerances of Predictions 4 and 8. Prediction 2's two adjacent contrasts are
  Holm-adjusted; nothing else is adjusted across predictions.
- Section 9 no longer says the thresholds come from no power calculation. The survival
  claims are the ones without one, and Section 9 says why.
- Prediction 5 scored two clauses on one line set carrying one no-effect rate, which is
  correct only for the mode clause: the ordering clause is not a Bernoulli event with a
  chance rate of one in four, so its alpha was meaningless as written. Section 7.1 now
  carries two rows, the mode clause anchored at .25 (a terminal mode among four
  candidates) and the ordering clause at 1/3 (the rate exchangeability gives the
  smallest of three pairwise distances when a pair's distributions share nothing), both
  on the 14-of-20 line: alpha 3e-5 and 9e-4, power .79 for each. Support requires both,
  so the prediction's error rate is no larger than either and nothing is adjusted
  between them; a split verdict is reported as indeterminate rather than as partial
  support.

The paper is 6,848 words / 16 pp (was 6,729); S1 is 5,090 words / 9 pp (was 3,943 /
7 pp).
