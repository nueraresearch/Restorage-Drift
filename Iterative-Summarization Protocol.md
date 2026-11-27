# **Restorage Drift in Iterative Summarization: A Test Protocol**

*Supplementary Material S1 accompanying “Restorage Drift: A Theory of Information State Evolution Under Repeated Compression and Reconstruction.”*

**Version 1.0.0 — 27 November 2026.** Pre-registration draft; no data collected.

## **1\. What this protocol is for**

Restorage Drift makes claims that are specific enough to fail. This document specifies how to make them fail in a system where the quantities of Section 5 of the theory paper can be measured directly: a language model that summarizes its own summary across repeated cycles.

Each of the theory's four state variables has an operational counterpart here. $K_n$ is manipulated directly, by what the stored text does and does not contain. $E_n$ is scored from that text by blinded coders. $A_n$ is estimated by recovery under a fixed probe procedure. $S_n$ is estimated by the distribution of probe responses. The first two are what the earlier draft of this protocol omitted, and without them the design tests reweighting while assuming the two mechanisms the theory was revised to separate.

The protocol is a companion, not an appendix. It is written to be pre-registered and run as an independent study, and it tests one instantiation of the framework rather than the framework as a whole. The phenomenon under test is restorage drift, in the theory's sense: drift that compounds because reconstructed output is written back as the state the next cycle operates on, instead of the record being preserved alongside it. Where the theory asserts that *some* $C$ and *some* $R$ operate under a resource constraint, this protocol fixes both and asks whether the resulting trajectory behaves as Section 5 predicts.

## **2\. The measurement problem**

Two design features determine whether the experiment measures anything, and both are easy to get wrong.

**The probe must not re-store.** Reconstruction is the operator under test, so observing a cycle cannot itself be a cycle. Each measurement is taken with a verification query whose output is scored and discarded: it never enters the stored state and never becomes input to the next compression. If probe output were fed back, the measurement would be a re-storage event and the observed trajectory would be the probe's, not the system's.

**Probe reactivity is a checkable assumption, not an axiom.** The design includes a low-frequency probe condition (measure only at cycle $K$) against the standard condition (measure every cycle). If $T_d$ differs between them, probing is causally implicated and the every-cycle measurements must be discarded in favor of end-point scoring. This condition is the protocol's own falsification test.

## **3\. Items and priors**

Each item is a short passage containing one target detail $x^{*}$ that is improbable under the model's prior, alongside a high-prior alternative that a reconstructive process could substitute for it. Items are matched on length and on the number of candidate variants scored (four per item), so that $m_n(x^{*}) < \tfrac{1}{2}$ measures the same event across items.

**Prior measurement precedes the loop.** For every item, $q = 20$ reconstructions are elicited from a stripped prompt that omits the record entirely but preserves the question. The empirical distribution over the four candidates is the estimate $\hat P$ used throughout. This is not optional: every prediction in Section 7 is stated relative to $\hat P$, so a protocol that skips it can only report that something moved, not that it moved toward the prior.

**Contamination screen.** An item is retained only if the stripped-prompt reconstructions recover $x^{*}$ at or near chance. Items where the model already knows the answer from training data measure recall, not reconstruction, and they are discarded before the loop begins.

## **4\. Arms**

| Arm | Question it answers | Manipulation |
| :---- | :---- | :---- |
| **A — Baseline chain** | Does drift occur at all? | $S_{n+1} = R(C(S_n), P)$ at budget $W$ |
| **B — Verbatim transport** | Is compression necessary? | Copy the record without paraphrasing: B1 identity when the record fits the budget, B2 mechanical truncation to $W$ |
| **C — Star topology** | Is re-storage necessary? | Each cycle recompresses $S_0$; no output is re-stored |
| **D — Shared-prior pairs** | Is the attractor prior-determined? | Item pairs with the same $\hat P$ but different $x^{*}$ |
| **E — Fictional items** | Where does the prior come from? | Items with no training-data prior; all prior structure supplied by the prompt |

Arm B and Arm C are the two controls the framework cannot survive without. Arm B isolates compression: if verbatim transport drifts, the mechanism is not compression. Arm C isolates re-storage: if the star condition drifts as far as the chain, accumulation across cycles is not what produces the effect, and the re-storage requirement of Section 2 of the theory is idle.

**Arm B in detail.** The control is only meaningful if it says what is copied when the record is longer than the budget, and a record longer than $W$ cannot be transported verbatim at $W$ without losing something. Arm B therefore splits. In **B1 (identity)**, items are constructed so the full record fits the largest budget and the entire record is copied unmodified at every cycle: nothing is dropped, nothing is paraphrased, and $C$ is the identity map. B1 asks whether re-storage alone, with no compression at all, produces drift. In **B2 (truncation)**, the record is cut mechanically at the token boundary to the summary budget and the retained span is copied exactly, under an instruction to reproduce it character for character. Truncation is lossy but not reconstructive: it removes content without asking the model to fill anything in.

Within B2, the position of $x^{*}$ is a controlled factor rather than a nuisance—either it falls inside the retained window, or it falls outside and is dropped. The two cases answer different questions. If $x^{*}$ is retained and still drifts toward the prior, reconstruction is operating on intact text, which is the claim that compression and reconstruction are separable. If $x^{*}$ is dropped, nothing about it survives the first truncation: under the absorbing-support assumption of Section 5.4 it leaves the active set, and reconstruction cannot generate a candidate that is no longer active, so $x^{*}$ cannot return at any later cycle.

Arm D is the sharpest test of the attractor claim in Section 5.5, provided the chains are matched on surviving candidates. Because the closed form's limit is a function of the prior and the retained set alone, two chains with the same $\hat P$, different starting points, and the same surviving set should converge on the same terminal distribution. Divergence under those conditions is evidence that the recursion is the wrong model even where drift is plainly present; divergence between chains whose surviving sets differ is the model's prediction rather than a failure of it.

## **5\. Conditions**

- **Budget** $W \in \{15, 30, 60\}$ tokens for the summary, held fixed within a chain and across its cycles.
- **Reconstruction length** fixed at $W_R$ across all arms, so that summary length is the only varying capacity parameter.
- **Probe frequency** every cycle (primary) or terminal only (reactivity check).
- **Compression mode**, crossed with arms where possible: paraphrase, orthographic perturbation, and qualifier deletion, corresponding to the three modes of Section 3 of the theory.
- **Target position** (Arm B2 only): whether $x^{*}$ falls inside or outside the retained window.
- **Sampling temperature** fixed and reported; model snapshot pinned by version string for the whole run.

## **6\. Measures**

All measures are computed from $m_n$, the distribution over the four candidates estimated from $q$ samples at cycle $n$: 20 by default, extended as described in Section 9 when the estimate lands near the one-half boundary.

- **Drift:** $d_n = 1 - m_n(x^{*})$.
- **Threshold:** $T_d = \min\{n : m_n(x^{*}) < \tfrac{1}{2}\}$, right-censored at $K$ when never reached. Censoring is a result, not a missing value, and it is analyzed as such.
- **Overtaking landmark:** $T_o = \min\{n : \exists\, y \neq x^{*}, \; m_n(y) > m_n(x^{*})\}$, the first cycle at which a rival's mass exceeds the original's. $T_d \leq T_o$ always, and the two coincide when only two candidates are scored, so $T_o$ is reported descriptively alongside $T_d$ rather than as a primary outcome: where they diverge, the gap is the interval in which the original retains a plurality but not a majority.
- **Attractor:** $\hat A$, the modal candidate at cycle $K$, compared against $\arg\max_x \hat P(x)$. Where $\hat P$'s modes are tied, the comparison is against the co-modal set rather than a single candidate.
- **Attractor distance:** total variation between terminal distributions of paired chains in Arm D.
- **Availability landmark:** $\hat T_A = \min\{n : x^{*} \text{ not recovered at cycle } n\}$, right-censored at $K$. A cycle counts as non-recovery only when none of the $q$ probe responses matches $x^{*}$ under the coding rule; one match is evidence that the candidate remains available. Because a finite probe can miss an available candidate, loss is required on two consecutive cycles before $\hat T_A$ is set, and single-cycle misses are reported separately rather than counted as recovery.

**Availability is a proxy, not the latent set.** $\hat T_A$ observes response behaviour under a fixed procedure. It is not $T_A$ of Section 5.6 of the theory, which is defined on the active set $A_n$, and the two diverge whenever the model can recover a candidate it no longer represents in the stored text. The operational quantity is therefore reported as "not recovered under the probe procedure" and never as "absent from the model".

**Evidence is scored independently of response frequency.** If $E_n(x^{*})$ were estimated from the proportion of correct responses, the evidence mechanism would be circular and the theory unfalsifiable. The stored summary of each cycle is therefore scored from its text alone, by two coders blind to arm, cycle number, and every probe response, on a four-point rubric: 0, no statement bearing on $x^{*}$; 1, the passage asserts a rival inconsistent with $x^{*}$; 2, the passage is compatible with $x^{*}$ but neither asserts nor excludes it; 3, the passage asserts or entails $x^{*}$. Coding is completed and frozen before response data are decoded, so that no coder can know which scores would favour which prediction. Disagreements of more than one point are adjudicated by a third coder, also blind. Agreement is reported as Krippendorff's $\alpha$ for ordinal data, and $\alpha < .80$ is treated as a failure of the measure rather than as a finding.

**From scores to a landmark.** With the operational threshold fixed at $\hat\varepsilon = 2$, a candidate counts as unsupported when both codings fall below "compatible". Let $\hat E_n(x^{*})$ be the higher of the two codings, so that the landmark fires only on coder agreement, and define $\hat T_E = \min\{n : \hat E_n(x^{*}) < \hat\varepsilon\}$, using the same two-consecutive-cycle rule and the same right-censoring at $K$. This is a text-level quantity. It becomes evidence about the model only if the response distribution moves with it, and Prediction 9 states what that requires.

## **7\. Pre-specified predictions**

1. **Directionality.** In Arm A at $W = 15$, $\hat A \neq x^{*}$ and $\hat A = \arg\max_x \hat P(x)$ in at least 30 of 40 items (75%); at most 20 of 40 (50%) is failure.
2. **Budget ordering.** $T_d(W{=}15) < T_d(W{=}30) < T_d(W{=}60)$ in paired comparisons within item. Support requires both adjacent hazard ratios below 1 with 95% intervals excluding 1; either at or above 1 with an interval excluding 1 is failure.
3. **Re-storage.** $T_d$ in Arm A is shorter than in Arm C at matched total token cost, and a share of Arm C chains is censored at $K$. Support requires a hazard ratio below 1 with a 95% interval excluding 1 and at least 20% of Arm C chains censored; a hazard ratio at or above 1 with an interval excluding 1, or censoring below 5% while at least half of the Arm A chains cross, is failure.
4. **Compression necessity.** B1 shows no threshold crossing ($m_K(x^{*}) \geq \tfrac{1}{2}$ throughout), and B2 with $x^{*}$ retained behaves like B1. B2 with $x^{*}$ dropped crosses at $n = 1$ instead: the detail is absent from the first summary rather than eroding across cycles, so $T_d = 1$. The later cycles reconstruct nothing: B2 copies the retained span character for character, so $x^{*}$ never re-enters the stored state, and any mass at $x^{*}$ in a later measurement comes from the probe generating it out of the model's prior rather than from the state. The contrast is the point—instant loss and gradual drift are different trajectories, and only the second requires the recursion. Support requires $m_K(x^{*}) \geq \tfrac{1}{2}$ in at least 95% of B1 chains, crossing in no more than 10% of the B2 chains that retain $x^{*}$, and $T_d = 1$ in at least 90% of the B2 chains that drop it. Crossing in 20% or more of B1 chains, in 40% or more of B2-retained chains, or $T_d > 1$ in 30% or more of B2-dropped chains, is failure.
5. **Attractor prior-determination.** Arm D pairs converge: in at least 75% of pairs the two terminal distributions are closer to each other than either is to its own starting state, and both lie within total-variation distance 0.20 of $\hat P$. At most 50% of pairs ordered, or a median distance to $\hat P$ above 0.35, is failure.
6. **Prior source.** Arm E drifts, but less than Arm A: fictional items retain $x^{*}$ longer because no training prior supplies the alternative. Support requires a hazard ratio below 1 with a 95% interval excluding 1 and a median $T_d$ difference of at least two cycles; a hazard ratio at or above 1 with an interval excluding 1 is failure.
7. **Mode sensitivity.** Orthographic and qualifier-deletion conditions cross at different $T_d$ than paraphrase within the same item: at least two cycles of difference in median $T_d$ for each contrast, in the same direction in at least 60% of items. Differences below one cycle in both contrasts, with intervals spanning zero, are failure.

8. **Availability order.** $\hat T_d \leq \hat T_A$ wherever both are finite, in every arm: a candidate with zero reconstructed mass has already lost the majority, so a chain reporting $\hat T_d > \hat T_A$ has a coding or decoding fault and is counted against the pipeline rather than reported. In B1 the record is identical at every cycle and $x^{*}$ is in it, so both landmarks are censored for most chains; in B2 with $x^{*}$ dropped, $\hat T_d = \hat T_A = 1$. Because this prediction is a check on the pipeline rather than a claim about drift, its criterion is a tolerance: at most 2% of chains may violate the order, and above that the arm is reported as a coding or decoding fault and no prediction is scored from it.
9. **Evidence precedes availability.** In Arm A at $W = 15$, $\hat T_E \leq \hat T_A$ with a lag of no more than two cycles, and both are censored in B1. A chain whose text support collapses while the response distribution holds is reported as candidate generation or parametric knowledge, not as evidence retention. Support requires $0 \leq \hat T_A - \hat T_E \leq 2$ in at least 70% of coded chains, and both landmarks censored in at least 90% of B1 chains; $\hat T_E > \hat T_A$ in 20% or more of coded chains is failure.

Prediction 2 depends on the coupling assumed in Section 5.7 of the theory, and stated there as a hypothesis—that a smaller $W$ raises $\beta$ relative to $\alpha$—rather than on the framework alone, so a failure of ordering bears on that coupling rather than on the recursion.

**From criteria to verdicts.** Each prediction now carries its own numeric criterion, so every result is scored as support, failure, or indeterminate — the last for any outcome in the band between the two, reported as such and counted as neither. Intervals are reported throughout: Wilson 95% intervals for proportions, hazard ratios with 95% intervals from the survival model of Section 8, and item-level bootstrap intervals for paired medians. The nine predictions are distinct claims rather than one global test, so no family-wise adjustment is applied and no composite score is formed; the count of indeterminate verdicts is itself reported, because nine unresolved claims do not constitute a test. A measured Krippendorff $\alpha$ below .80 voids the predictions that depend on the evidence score, before any outcome is examined.

The thresholds are set at the level a reader would need in order to act on the result, not at the smallest effect the design could detect. Thirty of forty items sits 3.2 standard deviations from a coin flip, two-sided $p \approx .002$; twenty of forty is chance exactly. The support and failure lines are therefore separated by a band the design can resolve, rather than by a rounding choice. Where the criterion is a hazard ratio the interval decides: a point estimate below 1 with an interval spanning 1 is indeterminate, not supportive, and is reported that way.

## **8\. Analysis plan**

$T_d$ is a censored time-to-event measure, so the primary analysis is a discrete-time survival model with cycle as the time axis: a mixed-effects logistic regression of crossing at cycle $n$ on budget, arm, and their interaction, with random intercepts for item and replicate. Chain and star are compared on the survival curve, not on mean $T_d$, because censoring makes means misleading when many chains never cross. $T_o$ is computed from the same distributions and reported descriptively; it is not modelled.

Attractor identity is analyzed separately as a categorical outcome at cycle $K$. Arm D is analyzed as a paired comparison of total-variation distances.

$\hat T_A$ is analysed exactly as $T_d$: discrete-time survival, same specification, with the paired difference $\hat T_A - \hat T_d$ reported per arm. The theory constrains the sign of that difference and nothing else about it, so the sign is checkable without fitting a mechanism, and a sign violation is a defect report rather than a result.

Evidence scores are fixed before outcomes are examined, and $\alpha$ is reported alongside them. Because coding is the expensive step while probing is the frequent one, the evidence measure is estimated on a prespecified subsample rather than on every chain: all cycles for three replicates per item and arm-cell, which yields $\hat T_E$ per chain with its precision reported.

The analysis plan, prediction list, item set, and prompts are to be registered before data collection. Because the theory's predictions are specific enough to be fitted after the fact, a study run without prior registration would not test them.

## **9\. Power, cost, and the minimal slice**

Replicates: $m = 10$ chains per item per condition; cycles: $K = 10$; probes: a base of $q = 20$ samples per measurement, taken every cycle in the primary condition and extended to 60 whenever the estimate lands in $[0.35, 0.65]$. The table prices that rule at an expectation of 20% of measurements in the band, which is $20 + 0.2 \times 40 = 28$ samples per measurement.

Measurement costs twenty times more than generation. An earlier draft of this section counted one probe call per measurement instead of $q$, understating the probe total by exactly that factor:

| | Minimal slice (4 items) | Full run (40 items) |
| :------------------------------------ | :---------: | :---------: |
| Summarization calls (6 arm-cells × items × 10 cycles × 10 replicates) | 2,400 | 24,000 |
| Probe calls (one measurement per cycle, 28 samples expected per measurement) | 67,200 | 672,000 |
| Total calls | 69,600 | 696,000 |
| Approximate tokens (about 110 per summary, about 100 per probe) | 7.0M | 70M |

Probes are about 96% of both calls and tokens, so this is a measurement budget far more than a generation budget, and the cheapest thing to cut is probe frequency rather than cycles or items. Money cost depends on the provider's per-token pricing and the input/output split; the token counts above are what to price.

A third cost does not appear in the table and is larger than either call count in person-hours: scoring. Two coders over the subsample described in Section 8 is 720 stored texts scored twice — 1,440 codings — for the minimal slice, and 7,200 texts scored twice — 14,400 codings — for the full run, at roughly a minute each, or about 24 and 240 hours. That, rather than the API bill, is what limits the evidence measure, and it is why the measure is subsampled rather than applied to every chain.

The 28 samples is an expectation, not a bound, and the assumption behind it is worth naming: the band is entered by cycles whose estimated mass sits near one half, which in this design is a minority, because early cycles sit near 1 and late ones near 0. If 10% of measurements land in the band the probe count is 57,600 and 576,000; at 30% it is 76,800 and 768,000; if every measurement needed the 60-draw ceiling it is 144,000 and 1,440,000. The minimal slice measures the actual share, and the full run is costed from it before the budget is committed, so the expectation is revised rather than assumed twice.



**That ratio exposes the design's real constraint.** With $q = 20$, the standard error of an estimated proportion near one half is $\sqrt{0.25/20} \approx 0.11$. A threshold decision at $0.5$ made on such an estimate will misclassify cycles close to the boundary, and because misclassification is most likely exactly where $T_d$ is determined, it can reorder conditions that differ by a single cycle. The protocol therefore samples sequentially: 20 draws first, extended to 60 whenever the estimate falls within $[0.35, 0.65]$. Most cycles sit far from the boundary—early ones near 1, late ones near 0—so average cost stays close to the low end while boundary decisions get three times the samples.

No formal power calculation is given, and the thresholds of Section 7 are not derived from one. The minimal slice is not scored against them — with four items, a 75% criterion is three items — it establishes feasibility, the share of measurements that land in the adaptive band, and the direction of effect. The full run at 40 items is what the thresholds are set for, including the budget-ordering comparison. Both are feasible on a single API budget without institutional resources, which is part of why summarization is the right test bed: Section 6 of the theory names it as an instance, so the cheapest available system is also one the framework claims.

## **10\. What this design cannot show**

- **One model is not a class of systems.** A result in one model family constrains that family. It does not establish drift in human memory, organizations, or cultural transmission, and the theory's cross-system hypotheses remain untested by it.
- **The evidence score is textual.** It measures support in the stored text, not evidence inside the model. Where text support and response behaviour disagree, the protocol can report the disagreement but cannot say which latent variable moved.
- **Summarization is not memory.** Nothing here bears on reconsolidation or on biological capacity limits; the token budget is a capacity parameter by analogy, not by measurement.
- **The items are not the Mandela Effect.** The protocol tests whether prior-favored variants displace improbable ones under repeated compression. It does not test whether any historical misremembering arose that way.
- **A null result does not falsify the framework.** It falsifies the claim that *this* $C$ and *this* $R$ produce drift under *these* budgets. The framework's generality is what makes it hard to kill, and this protocol is deliberately aimed at the narrow, killable part.
