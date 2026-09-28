# Tutorial content spine — draft 1

Deliverable of drunken-emu #17 (sub-issue of #16, the interactive-tutorial charter). Six chapters,
each with a stated message (same discipline `figbank` specs use), its live data source(s), and which
existing pattern it most resembles — a concrete target for #18 (interaction primitives), #19
(acceptance instrument), #20 (build harness) to build against, per #17's scope. Not final: the order,
the count, and any chapter's scope are all open to revision once #18–#20 land and it becomes clear
what an interactive primitive can and can't carry.

Every number below is a description of where a chapter's numbers come from at build/view time, not a
number itself — no figure in this doc, because this doc is not the tutorial.

## 1. One loop

**Message.** The maintainer is a reader that may also write: `MAINTAIN`, `EXPLORE`, `AGENT` are one
loop, not three (MetaProof `model/loop.md`; `model/definitions.md` §12.1).

**Data.** `model/loop.md`'s pseudocode block itself (static, quoted verbatim — a loop's definition
doesn't come from a run). The loop diagram already built and accepted (`fig4-agent-environment`,
MetaProof `figures/specs/`) is the visual anchor; this chapter is mostly that figure plus the
pseudocode, made steppable.

**Resembles.** The variable-model page's existing pattern (an accepted static figure, made
interactive by adding click-to-detail) — no new component class needed if #18's node+detail-panel
primitive lands first.

## 2. One episode, ablated

**Message.** Sufficiency and necessity are not asserted, they're shown: `experiments/demo/one_episode.py`
runs one seeded, deterministic, no-model-calls episode where every variable of the model takes a
value and gets knocked out one at a time — sufficient-by-construction, and each ablation's reported
change is the necessity argument.

**Data.** `experiments/results/one-episode-T0.json` (MetaProof) — already generated, has
`seeds`/`base`/`ablations`/`per_variable` keys. Live at view time: either re-run the deterministic
script at build time, or read the committed JSON directly (cheaper, and the episode is deterministic
so the two are equivalent — worth deciding explicitly in #20, not silently picking one).

**Resembles.** Nothing existing — this is the first real use case for #18's step-player primitive
(advance through ablations one at a time, each step re-deriving which defects appear/disappear from
the same JSON, never hand-typed).

## 3. Every variable, one home

**Message.** Every variable of the model has exactly one home, with its measurement status on it —
already built, already accepted (`variable-map`, drunken-emu ledger entry `MetaProof/variable-map`).

**Data.** `model/variables.json` via `bin/variables.py`, exactly as the existing page already does.

**Resembles.** Itself — this chapter is closest to a direct embed of `figbank/app/variable-model` as
one tutorial page, not a rebuild. Cheapest chapter to ship, good first target for #19 and #20 to prove
their harness against before spending effort on harder chapters.

## 4. The frontier, seen not counted

**Message.** A status-coloured tree makes an imbalance (0 sealed against 38 measured) visible at a
glance that `bin/frontier_refactor.py` had already found by counting — the same fact, seen instead of
computed (already the `frontier-tree` figure's own message, drunken-emu ledger).

**Data.** `MetaProof/ledgers/frontier.jsonl` live; the accepted static tree is the visual base.

**Resembles.** The tree + click-for-detail-panel pattern drunken-emu #12 is already building
(currently open, static-tree half delivered) — this chapter should consume #12's output directly
once it lands, not fork a second implementation.

## 5. How a figure earns its place

**Message.** A figure's acceptance is a record, not a chat: `bin/figpipe`'s validate → render →
rasterize → legibility → blind cold read → accept → log pipeline, dogfooded on the bank's own output.

**Data.** `figbank/ledger.json` (this track's own ledger, drunken-emu, just built) rendered live —
this chapter can show the actual current ledger table, not a snapshot, so it stays true as more
figures pass through the pipeline after the tutorial ships. `figbank/examples/pipeline-workflow.json`
(the `boundaries` figure of the pipeline's own seven steps) is the visual anchor.

**Resembles.** A live-data-table view, new: none of the existing pages render `ledger.json` yet. Small
scope — mostly plumbing `ledger.json` into a page, not a new interaction primitive.

## 6. Building this (self-application, closing chapter)

**Message.** Building a large interactive artifact with a coordinating team of sessions, a growth
gate, and an acceptance reader is itself a `MAINTAIN` run — the tutorial's own construction is a real
instance of chapter 1's loop, not a metaphor for it. Per drunken-emu #21's scope, this is deliberately
last: it needs real process (issues, commits, verdicts) to show, not a plan.

**Data.** The issue tree under drunken-emu #16 (this track), `figbank/ledger.json`,
`figures/verdicts.jsonl`, and — if this track ends up running with several sessions in parallel, as
the owner's charter anticipates — whatever coordination record that leaves (comments, competing
PRs/branches on the same sub-issue, `ledgers/log.md`-style entries).

**Resembles.** Nothing existing; explicitly out of scope until #17–#20 have produced enough of the
other five chapters that there is something real to narrate.

---

Open questions this spine surfaces for #18–#20, not answered here on purpose:

- Whether chapters 1–5 share one page (single-scroll, chapter = section) or are separate pages behind
  simple navigation — a build-harness (#20) decision, not a content one.
- Whether "live at view time" means client-side fetch of committed JSON (simplest, matches the
  zero-external-spend / self-contained-build constraint since the JSON ships in the same repo) or
  build-time injection (`__JSON__` slot, the existing `bundle.sh` pattern) — likely build-time
  injection for consistency with the rest of the bank, but #20 should decide and say why.
- Chapter 2's step player and chapter 4's detail panel are the two concrete first targets for #18;
  building against two real chapters rather than an abstract spec should keep the primitives honest.
