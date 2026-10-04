# Operation model: what a person actually does, step by step, and what it costs

emu-kit's original purpose: simulate the *person* using an artifact, not only the artifact's mechanics. Mechanics checks
(sizes, overflow, overlap) say nothing about why a real task took an hour. This model describes any task as a chain of
**primitive operations**, each with properties that make its cost visible, so chains can be recorded, compared, and checked.

Source case: a grader applying a correction to 66 students' grades on a phone (TapGrade, 2026-10-03), narrated step by step
by the person doing it. Every primitive below occurred in that narration.

## 1. Primitives

| Primitive | What the person does | Main cost |
|---|---|---|
| **ANCHOR(t)** | Jump to a target found without reading: screen edge or corner, fixed position, unique shape, the only card among text | ≈ 0 inference |
| **SCAN(S, k)** | Coarse-read a set S of similar items looking for keyword(s) k | O(\|S\|) shallow reading; errors grow with similarity |
| **READ(x)** | Fine-read one item to extract a fact | O(1) deep reading |
| **ENUMERATE(C)** | Make sure the candidate set in container C is complete: page through, check the seams between screens | O(pages) + holding "already seen" |
| **DISCRIMINATE(a, b)** | Tell two confusable items apart (`.js` vs `.json`, Review vs Re-sync) | 2+ memory slots, rereads |
| **HOLD(x)** | Keep a goal or fact in working memory across later steps | 1 slot per item, decays with time and with every other step |
| **KEYIFY(g)** | Compress a goal into the smallest key that survives: predicate / subject / object (`corrections` / `hw1` / `.json`) | one deliberate step; makes HOLD cheap |
| **RELOAD(g)** | Fetch a lost goal from outside memory (the chat, notes): itself a chain ANCHOR → SCAN → ANCHOR(heading) → READ → KEYIFY | high; triggered when HOLD overflows |
| **NAVIGATE(p)** | Open an app, page or view | includes RE-ORIENT on arrival |
| **RE-ORIENT** | Rebuild "where am I, what is on screen, what was I doing" after a jump, refresh or interruption | ENUMERATE(local options) + often RELOAD |
| **INFER(cause)** | Explain what the system shows ("why is there a list of changes? where did they come from?") | a wrong inference silently corrupts every later step |
| **WAIT(s)** | Wait for the system | uncertainty if there is no progress signal → REFRESH loops |
| **REFRESH** | Re-acquire system state | resets position → RE-ORIENT |
| **COMMIT(op)** | A consequential action (Apply, Delete, Save) | needs PREVIEW before and VERIFY after; irreversibility multiplies cost of error |
| **VERIFY(c)** | Check a claim. Two kinds: **consistency** (A matches B) and **correctness** (A matches intent) | consistency is cheap and often all that is offered |

## 2. Properties of each step (record these, not only the step)

- **anchor**: physical edge · fixed position · unique visual · text keyword · none
- **confusables**: how many look-alikes, and how alike
- **memory**: slots needed now, slots held across the step
- **reading**: none · coarse · fine, and how much
- **feedback**: immediate · delayed · none
- **reversibility**: idempotent · reversible · irreversible
- **interruption**: what is lost on refresh / app switch (position, goal, partial work)

## 3. Budget

Working memory is a budget B of a few slots, and **B is smallest exactly when help is needed** (tired, interrupted). When the
held items exceed B, a goal falls out and the chain gains a RELOAD, which is itself a chain. Most of the pain in the source
case was RELOAD and RE-ORIENT loops, not any single hard step.

Chain load ≈ reading + Σ(slots × steps held) + RELOADs + RE-ORIENTs + DISCRIMINATEs × similarity + WAIT/VERIFY loops.

## 4. The source case in this notation

**Cheap chain (save an artifact from chat; 2 effective steps):**
ANCHOR(card) → ANCHOR(⋯, top-right edge) → SCAN(menu, "Save … Files") → READ → TAP → ANCHOR(Save, top-right edge).
Every target anchored, the operation idempotent: nothing can go wrong, nothing to hold.

**Expensive chain (load the corrections file on the phone):**
NAVIGATE(site) → REFRESH → VERIFY(refreshed?) → REFRESH → RE-ORIENT → SCAN(tabs, semantic guess) → DISCRIMINATE(Settings,
Review, Re-sync) → … HOLD overflows → RELOAD(goal from chat: ANCHOR(last heading) → narrow paragraph → narrow sentence →
KEYIFY(corrections/hw1/json)) → NAVIGATE(picker) → ENUMERATE(folder, check seams) → SCAN(names) → DISCRIMINATE(js/json)
→ TAP → WAIT (no signal) → REFRESH → RE-ORIENT → INFER("loaded, so Apply") → SCAN for Apply → DISCRIMINATE (Scan first)
→ COMMIT → WAIT (no progress; view jumps to top) → REFRESH → RE-ORIENT → VERIFY(consistency only) → loop ×3 →
VERIFY(correctness: open questions, parts, students by hand, O(m + m²)).

**The wrong INFER that started it:** a list of changes appeared before the corrections were loaded, so the person inferred
"the system already knows the correction" — the only explanation available for "where did these changes come from".

## 5. Verifiers (what emu should check on a recorded chain)

Each is content-blind: it uses the step properties, not the meaning of the page.

1. **Anchoring**: every step that selects among options has an anchor other than reading; flag SCAN over look-alikes.
2. **Memory peak**: held slots never exceed B (default 3); flag any chain that needs RELOAD to finish.
3. **Candidate-set legibility**: the person can see that the option set is complete without ENUMERATE across screens.
4. **Interruption round trip**: after REFRESH or leaving and returning, position, goal and partial work are restored.
5. **Decision–information co-location**: at COMMIT, everything the decision depends on is on screen (what each row will
   become, not only that it will change).
6. **Progress continuity**: during WAIT the view does not move and progress is visible; a partial result says what is left.
7. **Causal legibility**: every list or prompt says where it came from and what is not yet included (no wrong INFER).
8. **Single path**: one action per intent; two views that do the same job (Re-sync, corrections) are one finding.
9. **Correctness after commit**: the system re-reads the target and reports correctness against intent, not only that
   "everything matches".
10. **Separators carry structure**: block boundaries (a key vs the grader's note) are visible without reading content.


## 6. Where this sits in emu (read with `docs/EXPLORE-SPEC.md`)

This model is not a second explorer. It is the per-step anatomy of `explore`'s decision records, plus the one piece
EXPLORE-SPEC's implemented layer says it does not do yet: **working-memory limits need decider-side memory** (the scripted
policies read the page instead of remembering).

| EXPLORE-SPEC knob | primitives here | what it adds |
|---|---|---|
| `--working-memory N` | HOLD with budget B = N slots; KEYIFY to fit a goal in one slot; RELOAD when a goal falls out | the decider keeps keys, not the page; RELOAD is a recorded detour with its own cost |
| `--distractibility p` | SCAN hijacked by the most salient look-alike | the confusable count and similarity of the step |
| `--patience k` | WAIT without a progress signal → REFRESH → RE-ORIENT | why patience runs out: no feedback, lost position |
| `--impulsivity` | READ truncated; COMMIT without PREVIEW | the reversibility of the step decides the damage |
| `--salience-driven` | ANCHOR by salience instead of by an intended landmark | anchor type of the step |

Two uses, one record format:

1. **Simulated**: `explore_run` deciders keep a slot store (HOLD/KEYIFY) of size N and must RELOAD from a named external
   source (the task text) when a needed key is gone; every RELOAD and RE-ORIENT is a step in the trace. The sweep then shows
   how goal-achievement and false completions change with N.
2. **Recorded**: a person's narrated chain (the HW1 correction pass) written in the same step format is a fixture: the
   verifiers in section 5 run on it, and a policy reproducing it should hit the same RELOADs.

Open problem: `P-2a7c` in `docs/OPEN-PROBLEMS.md`; issues #31–#40.
