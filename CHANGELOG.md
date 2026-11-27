# Changelog

All notable changes to Restorage Drift are recorded here. The manuscript's own
version line is kept in step with the release tag, so a reader holding a PDF can
tell which release it came from.

## [1.0.0] — 2026-11-27

Initial release. Theory paper plus Supplementary Material S1. No empirical data.

### Paper

- Theory paper at 17 pp, 7,002 words, within a 7,500-word limit.
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
- The note under that table claimed alpha never exceeds .008, which Prediction 7's
  .0083 line contradicts. The bound is corrected and the note now carries every row's
  alpha and beta (1: 1.1e-7 and .005; 5a: 3e-5 and .0039; 5b: 8.8e-4 and .0039; 7: .0083
  and .001; 9: 1e-27 and .0059), so a reader can still check each error rate now that
  those two columns are gone.
- That list was itself stale in two places, which the check below caught. Prediction 9's
  entry still carried the alpha and beta of the 400-chain version, and the "largest
  beta" sentence pointed at Prediction 1 when Prediction 9's is larger. Both are
  corrected: 9 reads 1.0e-27 and 5.9e-3, and the maximum is .0059 at Prediction 9.
  Rather than leave the next reader to find this, `check_thresholds.py` recomputes every
  row's alpha, beta and power from its unit count, no-effect rate and line, and compares
  them with the table, the note and the prediction text. `build.py` runs it first and
  refuses to make a PDF when they disagree. Four deliberate mutations — a table count, a
  note rate, a prediction count and a power cell — each stop the build.
- The Section 9 cost table was the last block of derived numbers without a guard, and it
  had already drifted once when the adaptive probe rule was folded in. The checker now
  recomputes it too: summarization and probe call counts, totals, token estimates, the
  10% and 30% band shares, the 60-draw ceiling, the probe share of calls and tokens, and
  the coding hours, all from the stated design (6 arm-cells, 10 replicates, 10 cycles,
  20 and 60 draws, 110 and 100 tokens, 40 or 4 items). Counts are compared exactly and
  only the rounded millions get a tolerance, which is what let two off-by-a-few-hundred
  call counts through on the first attempt. The design sentence and the 20 + 0.2 x 40 =
  28 rule are anchored as well, so changing a constant in one place fails. Twelve
  deliberate mutations, including a call count, a total, a band share and a coding hour,
  each stop the build.

- Word and page counts are now checked too, in README, CHANGELOG, RELEASE_NOTES and
  .zenodo.json, and doing it exposed a real error: the counts had been measured with
  `sed ... | wc -w` under the shell's default locale, which for multibyte text does not
  agree with a UTF-8 locale. It gave 6,848 against 6,853 for the paper and 5,142 against
  5,167 for S1, so every quoted word count was slightly low. The canonical definition is
  the checker's: strip the LaTeX blocks, split on Unicode whitespace, independent of
  locale. Pages are read from the built PDFs, which is why `build.py` runs the check
  before the build with `--skip-pages` and again after it.

- Section 5.6's landmark ordering was stated without its proof, and two reviews read it
  as false with four candidates. It is not: a rival that exceeds the original forces the
  original below one half, because the two shares sum to at most 1, so majority loss
  cannot follow overtaking. What four candidates do allow is the reverse gap, and the
  passage now says so with the (0.4, 0.2, 0.2, 0.2) case in the text, where no rival
  overtakes and the second landmark is infinite. Section 6 of S1 states the same convention. The same
  review objected that Section 3's examples are not evidence; the closing sentence said
  they "show" the pathways, and now says they illustrate them.

- S1 required the item set and prompts to be registered but never said what would be registered,
  so Section 3.1 now specifies the item record: the JSON Lines schema and its seven fields, the
  probe as a single stripped-prompt turn over the four candidate labels with unmatched replies
  kept as `none` in the denominator, and ground truth as a target label plus character span
  checked by script. The set itself is `items.jsonl` in the registration pack, identified by
  SHA-256 in the registration and released with the first analysis, for the reason the
  contamination screen exists: item text in this repository would sit in the training data of
  any model that later reads it. No item text is included here.

- Zenodo holds one licence per record, so the deposit could not honestly carry the old
  split ("text and figures CC BY 4.0; build scripts MIT"): the archive contains both, and
  the record-level field would have contradicted the LICENSE inside it. The record is now
  CC BY 4.0 in its entirety, with MIT as an additional option for the build scripts rather
  than a carve-out, and LICENSE says so instead of "two licences, by file type". While
  rewriting it: check_thresholds.py was missing from the MIT list (three of four scripts
  were named) and Human Restorage Study.md was listed although it is not in the record. A
  separate scripts record was considered and rejected, since the deposit is the tag tree
  and the scripts would stay inside the paper's archive either way.

- .zenodo.json was the last derived artifact with no guard, and two reviews reported it
  broken when it was valid. `build.py` now checks it before anything is built: it must
  parse; it must carry title, description, publication_date, access_right, license and
  upload_type, plus publication_type when upload_type is publication; the date must be
  ISO, access and type must be in Zenodo's controlled vocabularies, and every creator
  must have a name and a well-formed ORCID. Nine mutations each stop the build with the
  field named.

- The deposit dry run now has a versioned record, `DEPOSIT.md`: the 20-file inventory
  with per-file sizes and the 1,719,125-byte total measured at a4f130d, the commands
  that show S2, the registration draft and build intermediates absent from the index, and
  which schema validated the metadata and why the strict one is not the test applied.
  It names commits instead of saying "current", so each figure can be re-derived.

- The contamination screen was the last unquantified exclusion rule: it kept items whose
  stripped-prompt recoveries were "at or near chance". With four candidates and q = 20,
  chance yields 5 of 20 on average with a standard deviation of 1.94, so Section 3 now
  discards an item at 9 or more recoveries (chance alone: p = .041, one-sided at .05) and
  keeps it at 8 or fewer, fixed before any full-text run; Section 3.1 records the verdict
  in `screen`. The checker recomputes the threshold and the tail from the binomial and
  fails the build if either drifts from the text.

- Section 7 said only that the nine predictions are distinct claims and were not
  adjusted, while the predictions carry five count-based rules at .01: nine directional
  claims leave the family-wise error near .09. The five rules are now one family of four
  hypotheses (5a and 5b joined by intersection-union), Holm-Bonferroni at .05 with steps
  .0125, .0167, .025 and .05; 2, 3 and 6 stay interval estimates and 4 and 8 tolerance
  lines, outside the family. Because .01 is stricter than the first step, every power in
  the table is a lower bound, and 7.1 now says so. The checker derives the four steps and
  fails the build if the rule, its family size or that bound claim goes missing.

### Registration reconciliation pass (27 November 2026, before deposit)

- `Registration Fields Draft.md` had drifted from S1 a second time: it still set alpha at
  .05, put all nine predictions into one Holm family, and defined "a substantial share"
  of censored Arm C chains as one half where Section 7's support line is 20%. It is now
  derived from the protocol — per-row alpha at .01 with the achieved maxima .0083 and
  .0059, one family of four with the same four Holm steps, and the five count lines quoted
  as Section 7.1 states them. The four-item slice and the 40-item run were already the
  protocol's own figures and are unchanged.

- The draft is working material and stays outside the archive, so no step in the build
  ever looked at it. `check_thresholds.py` now carries `check_registration_draft()`, which
  regenerates the draft's figures from the constants that hold the protocol — the same
  rows, slice size, screen and cost model — and fails the build when one disagrees. It
  runs only when the file is present, so a clean clone still builds; a number that no rule
  claims is itself an error, which is what catches a third drift being written in rather
  than merely repeated.

- `DEPOSIT.md` records the draft's SHA-256 and byte size, so the text that would be
  registered is tied to this deposit by content even though the file is held outside the
  archive and cannot be obtained from the DOI. The same guard hashes the file, compares
  both values with that table, and fails when either disagrees; in a clean clone neither
  the file nor any way to verify it is present, and the check reports the skip it already
  reported for the rest of the draft.

- The draft gained the field S1 leaves out: where the run's output goes. Raw chains, probe
  outputs and scores are named by file, format and release point — JSON Lines with a
  manifest carrying each file's digest, released at the end of collection and again at
  coding freeze — with the archive itself marked [decision], since the protocol fixes
  where the item set lives and says nothing about anything produced from it. The draft's
  recorded digest and byte size in `DEPOSIT.md` were updated to match, and the guard
  compares them, so the two cannot drift apart.

- The paper and S1 now say what data exist and where the item set lives. The paper's
  data-availability paragraph said only that materials would be deposited "upon execution";
  it and a new Section 11 in S1 now state that no data were collected, that `items.jsonl`
  travels in the registration pack with its SHA-256 recorded there and is released when the
  first chain is analysed rather than published in the repository — since item text beside
  the theory would enter the training data of any model reading it, defeating the screen
  that makes the set usable — and that the chains, probe responses and scores are
  deposited with the analysis code when the run executes.

- `README.md` told readers the registration draft's bracketed thresholds "have not been
  justified" and not to register it. Both claims had expired: the figures are S1's own and
  are re-checked on every build made where the file exists. The bullet now says that and
  names the three values still open — the model snapshot, the output archive and the
  chain-exclusion threshold.

- `.zenodo.json` carried no `related_identifiers`, so the record named nothing it was built
  from. It now points at the repository tag, with `isDerivedFrom` and the source's type;
  `check_metadata()` validates the identifier, the relation and the resource type, and
  fails the build when the list is missing or malformed. A record cannot relate its two own
  files to each other, so S1's status as a supplement is carried by the file list and the
  description; the version relation to the DOI-bearing release belongs on v1.0.1.

### Probe-proxy and Prediction 1 null correction (27 November 2026, before deposit)

- Prediction 1's no-effect rate was the four-way floor of .25, which is Prediction 5a's
  null: there the mode contest is against all four candidates. Prediction 1 compares the
  terminal mode with x* alone, so a system that lost the detail still chooses among four
  candidates and may prefer the prior's mode for reasons that do not involve re-storage.
  The null is one half, a contest between the prior's mode and the target, and the line
  moves from 26 of 40 against 22 to 28 of 40 against 23. The old line rejected .5 at
  .040, outside the .01 ceiling; the new one rejects it at 8.3e-3, with failure at 23.
  Power falls from .95 to .82 at p1 = .75, which is what forty items buy at this null.
  Arm B1 is named as the reported empirical check rather than as the anchor, because a
  confirmatory line cannot be set from data the study has not collected.
- Section 6 now says what the probe measures. m_n is a distribution of answers under one
  fixed procedure applied to a stored text, while S_n is a distribution over candidates
  internal to the system; the two coincide only if the text is doing the work the theory
  attributes to it, which is what Prediction 9 tests. Every verdict in Section 7 is
  therefore a claim about response behaviour given the stored text, and none of them is
  a claim about the model's internal state. Prediction 1's wording is narrowed to the
  probe's modal answer for the same reason.
- The four-way floor is no longer reported as a second significance level beside the
  null. It changed no decision, and it duplicated 5a's null; a second inline alpha is a
  second number to keep in step. Section 7.1's rationale was rewritten shorter, and the
  null-behaviour and failure-line paragraphs were reworded to match the one-half rule.
- The checker gained three guards, each mutation-tested against a deliberately broken
  input. It rejects any control byte in the prose: two heredoc casualties in the same
  paragraph (`\a` arriving as 0x07 where `\alpha` was meant, and `\t` arriving as 0x09
  inside `\times`) each survived a reading of the text, and one survived a first byte
  scan that still allowed tabs. It recomputes both inline alphas in 7.1's correction
  paragraph at the .5 null, at 2% rather than the 12% used for table values, since a
  quoted 9.3e-3 would otherwise pass against a computed 8.29e-3. It also holds
  `DEPOSIT.md`'s reproduce block to the draft it prints, not just the table above it,
  where the two had drifted apart.

### Item-set naming (27 November 2026, before deposit)

- S1 Section 3.1 and Section 11 promised the item set as one file named `items.jsonl`, and
  the paper's data-availability paragraph repeated it, but the registration pack holds two
  construction sets: `items.pilot.jsonl` (eight fictional items) and `items.real.jsonl`
  (eight real-world ones), each with a manifest carrying its SHA-256, byte size and record
  count. Those are the names its own builder writes and its construction standard
  describes; the single fixed name was the outlier, and it was a promise the pack could
  not keep. Renaming one file to `items.jsonl` would have dropped a stratum, and merging
  two unmeasured sets would have registered one digest over text that was never screened,
  so the documents moved instead: S1, the paper and the registration draft now name the
  sets the pack holds, in the pack's own per-set convention, and the registration records
  the digest of each set it registers rather than of a file that does not exist.

- Nothing about the promise's substance changed. The item text is still absent from this
  repository and from the archive, still identified by digest, and still released at first
  analysis, for the reason Section 3 gives: item text beside the theory would enter the
  training data of any model that later reads it, which is the contamination the screen
  exists to detect. `DEPOSIT.md` records the registration draft by content, so its digest,
  byte count and line count moved with the draft.

- `check_thresholds.py` now holds the names together, because a name repeated in three
  documents is exactly the kind of claim that drifts. It fails the build when the
  protocol, the paper or the draft names no item-set file, when one of them still says
  `items.jsonl`, or when they name different sets; where the pack is present it also
  requires each named file and its manifest on disk, and each manifest's digest and byte
  count to match the file beside it. A rebuilt or renamed set is therefore a build error
  rather than a stale sentence in the protocol. The guard skips the pack on a clean
  clone, as the draft guard already does.

The paper is 7,006 words / 17 pp (was 6,925 / 17 pp); S1 is 6,655 words / 11 pp (was 6,061 / 10 pp).
