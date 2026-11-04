# What a record of a person's task must be: theory, tried on one real task

*Theory track (chat session), branch `theory/record-model`, 2026-10-04. A brainstorm: not merged, not a format. Every
claim is a hypothesis with its falsifier. The worker (Claude Code) implements; this file gives test points, not
prescriptions. Instruments: `proto.py` → `RESULTS.md`, `liveness.py` → `LIVENESS.md`, both on
`docs/evidence/hw1-correction-2026-10-03/` (the narration, verbatim, and its transcription).*

## 1. The problem

emu records tasks as chains (C5, PR #43): one flat list per task, one value per property, defaults for silence. A record
must let us **predict** where a person will struggle on an artifact and **check** the prediction against what happened
(#32: T1–T10). The question is what structure makes both possible without the check being circular.

## 2. Model

**L0 sources.** Immutable, content-addressed: narration text, screenshots, logs, captured page states.

**L1 assertions.** Each is a tuple

    (subject, predicate, value, role, asserted_by, encoded_by, modality, scope, evidence, at?)

- *subject*: an occurrence (goal, step, event), an object (surface, control, item), or `world`.
- *role*: what kind of claim it is (section 3): `predictor`, `behaviour`, `outcome`, `belief`, `state`, `opinion`,
  `structure`, `world`.
- *asserted_by*: who holds it true (the narrator, a screenshot clock, the artifact's code, a transcriber, a policy,
  a judge model). *encoded_by*: who turned it into this tuple. They differ: the narrator states "固定位置", the
  transcriber encodes `anchor = fixed-position`. Fidelity of encoding is checkable (the quote is verbatim); truth of
  the assertion is a different question.
- *modality*: `stated`, `measured`, `designed`, `inferred`, `simulated`, `judged`.
- *scope*: a run, or a pattern ("what usually happens"); instances link to patterns.
- Structural predicates: `part_of` (a DAG), `before` (a partial order), `at` (a time or interval), `because`
  (an outcome attributed to a cause), `believes` (an agent, a proposition, a time), `instance_of`.
- Append-only. Conflicting assertions coexist.

**L2 views.** A chain in C5's shape, a goal tree, a memory timeline, a cost estimate, verifier findings: each derived
deterministically from L1 under a **lens**.

**Lens.** Which asserters and modalities are admitted, how conflicts resolve, and what silence means. Silence has three
readings that must not be confused: *not asserted* (unknown), *asserted absent*, *default*. A lens that fills silence
with defaults must say so; its findings carry that.

**Verifiers are three-valued:** FINDING, PASS, UNDECIDED. A verifier is **monotone** if adding admitted assertions can
turn UNDECIDED into a decision but never flips a decision. Monotone verifiers make findings robust: a finding decided
under a small lens survives every larger one. Default-filling breaks monotonicity (a default PASS flips to FINDING when
the real value arrives), which is exactly P-02be.

## 3. Role separation: predictors are inputs, outcomes are held out

A narration mixes five kinds of statement. From the HW1 account:

| Role | Example (verbatim) | Source it should come from |
|---|---|---|
| predictor: a property of the artifact or situation | 固定位置，有手机屏幕物理边界作为nav anchor; 一堆长得差不多的乱码 | the artifact (measured or designed); the person's statement is one witness |
| behaviour: what the person did | 一屏一屏首尾相接地翻完整个folder | narration, capture |
| outcome: what happened to the person | 4-bit内存就已经烧得差不多了; 忘记我是来干嘛的了; 走个过场 | the person only |
| belief | 只可能是已经知道有correction的需求了 | the person only |
| opinion | 无论是空一行还是用【comment】 | the person only |

**Claim 1 (leakage).** A verifier that reads outcomes as inputs restates the person's complaint and cannot fail. C5's
`interruption` key ("what an app switch loses") and OPERATION-MODEL's step properties mix outcome into predictor. The
check is only meaningful when verifiers read predictors and are scored against held-out outcomes.
*Falsified if* verifiers fed with outcomes predict new tasks no worse than verifiers fed with predictors only.

**Claim 2 (source).** Predictors should be measured from the artifact; outcomes and beliefs can only come from the
person. Narration is a weak source of predictors for the run itself (below), and a strong source of outcomes.

**Claim 3 (polarity and attribution).** Outcomes have a polarity (ease: "边际成本为0"; friction: "烧得差不多了") and
must be attributed to causes (`because`). Both were missing from the first analysis and changed its results.

## 4. Structural diagnostics on the HW1 task (`RESULTS.md`)

**What these numbers are and are not.** Roles, polarity, attribution and normalised values were all assigned by hand,
and the structure itself is still a hypothesis. So the numbers below are not measurements of how good a verifier is.
Their only use is diagnostic: they show **which structural choices change the conclusions** (defaults, roles,
attribution) and therefore must be settled, recorded and argued before anything is measured. A number that moves when
an unrecorded choice changes (agreement under two attribution rules, below) is a sign that the structure is not yet
there, not a result.

54 trigger points of ten verifiers (plus a label check) in the run itself; outcomes held out.

| lens | decided | agree / disagree (goal attribution) | agree / disagree (window attribution) |
|---|---|---|---|
| S: narrator-stated predictors | 8 of 54 | 7 / 1 | 5 / 3 |
| A: artifact-sourced predictors | 3 of 54 | 3 / 0 | 2 / 1 |
| SA | 11 of 54 | 10 / 1 | 7 / 4 |
| SAI: plus transcriber inferences | 15 of 54 | 14 / 1 | 9 / 6 |
| D: plus C5's defaults | 54 of 54 | 15 / 39 | 35 / 19 |

**Robust (holds under both attributions):**
1. *Defaults manufacture contradictions*: 19–39 of 54 decisions contradict the outcomes under lens D, against 1–6 for
   lenses without defaults. The memory verifier alone passes 27 steps by default where goal loss was reported.
2. *Narration cannot decide most run steps*: 8–15 of 54 decidable without defaults. The run part of the account states
   13 predictors, the generalised part 16: describing "what usually happens", the person describes the artifact;
   describing this run, the person describes what happened to them.
3. *Artifact facts decide what narration cannot*: single path (two views for one intent) and correctness-after-commit
   (the scan compares with the bank, never with intent) are undecided under S and decided under A.
4. *A wrong belief is locatable*: D3, 13:00, believed `corrections_loaded = true`; the 13:00 screenshot shows false.

**Sensitive, so not yet meaningful:** agreement rates move with the attribution rule (S: 7:1 vs 5:3). Attribution is a modelling question, not
a reporting choice, and must be recorded (`because`, with its asserter) rather than chosen by the analyst afterwards.

## 5. Working memory as register pressure (`liveness.py` → `LIVENESS.md`)

No one states the contents of their working memory, so the memory verifier is undecided under every lens without
defaults. It needs a predictor-level model. Proposal: the compiler's.

| Task | Compiler |
|---|---|
| an item produced on one surface and needed on another (which file, which view, the step order) | a variable, live from definition to last use |
| working-memory slots (a few; fewer when tired) | registers |
| items live at once | register pressure |
| losing an item, writing it down, fetching it from the chat | spill and reload (RELOAD) |
| the needed item shown again on the surface where it is used | rematerialisation |

Consequences:
- Pressure is computable from the task's dataflow and the artifact (what each screen shows), before any person uses it:
  a non-circular predictor of goal loss.
- *Co-location* (OPERATION-MODEL §5.5) is rematerialisation: the verifier and the memory model are one mechanism.
- Complexity: for a fixed order, liveness is linear in the number of steps. Choosing an order that minimises peak
  pressure is register sufficiency, NP-complete in general (Sethi 1975) and polynomial for trees (Sethi and Ullman
  1970). Tasks that nest as goals are close to trees; design questions of the form "can this flow be ordered so that
  nothing must be carried" are answerable for them.

**Trial on HW1.** Seven items encoded by hand; five losses reported (held out).

| B | reported losses within or right after predicted high pressure | high-pressure steps away from any loss |
|---|---|---|
| 2 | 5 of 5 | 8 |
| 3 | 2 of 5 | 7 |
| 4 | 1 of 5 | 4 |

The narrator's own estimate ("工作记忆只剩3 bit" when tired) is consistent with a small B. **This is not a validation:**
the items were encoded after reading the outcomes (one, "the step order", is consumed exactly where the narrator twice
forgot to scan), and B was chosen on the same data. It shows the model can express spills; the test is section 8.
Precision is low because pressure persists over stretches while a loss is an event; onset of pressure, not its
duration, is the candidate predictor.

## 6. Order is partial

Narration order is not time: the account's generalised paragraph comes before events of 12:59–13:00; only screenshots
anchor the clock. Order-dependent measures (peak pressure, loss onsets) are therefore ranges over the linear
extensions consistent with `before`. Exact range: NP-hard in general (it contains register sufficiency); for
series-parallel orders, a dynamic programme over the decomposition; for a narration (long sequences with few
uncertain interleavings), enumeration is enough. *Falsified as a concern* if, over several narrations, conclusions never
change across extensions.

## 7. Aligning two records (T3)

The same task on two versions of an artifact, or a person against a policy: align goal trees by tree edit distance
(Zhang and Shasha 1989; APTED, Pawlik and Augsten 2016), with label costs from intent equivalence. Whether "Re-sync" in
0.6.5 and "Update Canvas" in 0.6.6 serve the same intent is a semantic judgment: a judge model (or the owner) asserts it,
with modality `judged`, and the alignment cites the assertion.

## 8. Prediction, pre-registered (T10, E5)

The only test that can fail.
1. Before the owner's next real pass (the HW2 blind sample in TapGrade), from the task design and the artifact:
   the dataflow items (section 5), predictors measured on the artifact (section 9), B fixed in advance, predicted loss
   onsets and friction per segment with probabilities, and the predicted ranking of segment durations.
2. Commit it (the commit time is the registration).
3. After the pass, the owner leaves a narration and screenshots as on 2026-10-03; transcribe as before.
4. Score: Brier score of the segment predictions; Kendall's tau between predicted and measured segment durations;
   onsets hit within two steps.
One task is weak evidence; the protocol accumulates across tasks, and each new account is held out until scored.

## 9. Measuring predictors on the artifact

| Predictor | Content-blind measure | Needs a semantic reader |
|---|---|---|
| anchor type | position invariance of a control across states; distance to a screen edge; visual uniqueness among same-role controls | |
| confusables | same-role controls in view with similar labels and geometry | whether they are confusable for this intent |
| feedback | DOM or visual change within a short time after an action | |
| view stability | scroll and position changes of the focused region during an operation | |
| separators | block boundaries in rendered text | |
| label ↔ intent | | does any label say what this task wants ("update")? |
| origin stated | | does a list say where it comes from and what it does not include? |

The right-hand column is legitimate: semantic judgments are what this kit exists for. A judge model is an asserter with
modality `judged`; its judgments are kept apart from measurements and can be checked against people.

## 10. Falsifiers, in one place

- Outcome-fed verifiers predict new tasks as well as predictor-fed ones: role separation is not needed.
- Stated and inferred predictors never lead to different findings: lenses can collapse.
- Conclusions never depend on the linear extension: order can be a sequence.
- Pre-registered pressure onsets do not hit reported losses better than chance across tasks: the memory model is wrong.
- Artifact-measured predictors disagree with the person's statements about the same controls more often than they agree:
  the measures do not capture what people perceive.

## 11. For the worker (test points; implementation is yours)

| # | Test point |
|---|---|
| E1 | Every informative span of the narration is covered by an L1 assertion; uncovered spans are judged tone only. |
| E2 | Under lenses S, SA, SAI and D, findings are reported with the lens; findings that exist only under D are listed as P-02be instances. (`RESULTS.md` is a first run.) |
| E3 | Order-dependent measures are reported as ranges over consistent extensions. |
| E4 | The load model's ranking of segments matches clock-anchored durations (13:06→13:30 loading, about 24 min; 13:30→13:48 applying, about 18 min), or P-67a1 has a counterexample. |
| E5 | Section 8, before the HW2 sample pass. |
| E6 | TapGrade's save history and Canvas data enter as measured sources and agree with the narration and screenshots on the same events. |
| E7 | The memory verifier decides from dataflow pressure (section 5) without defaults; items derived from the task design. |
| E8 | Outcomes carry polarity and `because`; the agreement table is reported under each attribution until `because` is recorded. |
