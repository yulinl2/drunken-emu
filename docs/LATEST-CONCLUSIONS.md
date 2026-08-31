# Latest conclusions

*v0.1.2 · 2026-08-31 · maintained*
*Provenance: folded from the build sessions of 2026-08-22 → 08-31 (MetaProof
Project). Superseded rows move to README `## Falsified`, never deleted here
silently.*

One line per settled conclusion, strongest evidence first. Tags per the writing
contract: `[FACT]` verified by running something · `[JUDGMENT]` reasoned, not
mechanically checkable.

## About this kit

- `[JUDGMENT]` **The name is the specification.** Impaired executive function
  presents externally like drunkenness; the target reader model is
  intention-plus-degradation. Not self-deprecation about current code.
- `[FACT]` Current `blind_audit.py` is intention-less: 4 taps, one hardcoded
  pixel, recursion depth 0, zero feedback into later decisions. Counted, not
  estimated.
- `[JUDGMENT]` Proxy calibration is three-way: `blind_audit` under-powered,
  a competent explore agent **over**-powered (passes what real readers fail),
  impaired-explore calibrated. The middle option is the rejected one.
- `[JUDGMENT]` The anti-leak rule decomposes: content-blindness (keep) ⊥
  intention-lessness (gap). Conflating them is Falsified row 3.
- `[FACT]` Mount cost is linear in DOM nodes, not source bytes: 80 KB of
  comments (2 nodes) mounts faster than 19 KB of 500 spans, in every
  environment tried.
- `[FACT]` The linear *constant* spans 0.122–0.55 ms/node across **four**
  environments (4.5x). CI therefore asserts orderings and R², never constants
  — first CI run on a foreign runner passed 6/6 because of this choice.
- `[FACT]` **The slope is not stable within one machine either**, which changes
  what the cross-environment spread means. Six consecutive runs of
  `ci_claims.py` in a single claude.ai container, no code or fixture changes:
  **0.274 · 0.212 · 0.200 · 0.193 · 0.215 · 0.228** ms/node — a 1.42x ratio
  from the same hardware in one sitting. The first reading of a session is the
  outlier every time (cold Chromium, cold page cache), so a single measurement
  systematically over-reports.
- `[JUDGMENT]` Consequence: "0.122–0.55 across four environments" cannot be
  read as four environment-specific constants. Roughly a third of that 4.5x
  span is reproducible within one box, so the between-environment component is
  smaller than the interval suggests and no single number characterises any one
  environment. This *strengthens* the P3 resolution rather than weakening it —
  asserting orderings and R² was correct for a reason stronger than the one
  originally given.
- `[JUDGMENT]` Method note, self-inflicted: the fourth datapoint was written
  into this file as a settled `[FACT]` from **one** run, then corrected within
  the same session when a routine regression produced 0.212. The project's own
  rule — sample twice before writing it down — was violated by the session that
  had just re-read the rule. The rule needs a mechanical home, not a prose one.
- `[JUDGMENT]` Falsified entries split by species: wrong **numbers** die by
  re-measurement; wrong **justifications** propagate by being quoted. The
  ledger must hold both, and the second kind is the dangerous one.

## About the environment (details: SANDBOX-FACTS.md)

- `[FACT]` No daemon can exist in a claude.ai container; the only real uptime
  is GitHub Actions. This constraint shaped the entire sync design.
- `[FACT]` Single observations of cached/async/lazily-indexed systems are not
  facts. Four single-read conclusions in this project were later reversed.

## About process

- `[JUDGMENT]` Committed files are the sole stateful interface between
  sessions. The container is scratch plus secrets; the conversation is
  volatile. Anything worth keeping is worth a commit.
- `[JUDGMENT]` Docs carry version + provenance headers; version numbers anchor
  deployed history, never conversation history.
- `[JUDGMENT]` `main` receives settled states only; iteration lives in local
  commits; branches coordinate between agents, never between one agent's
  drafts. Full statement: `CONTRIBUTING.md`.

## Loop of 2026-08-30 (second branch)

- `[FACT]` The container volume survives conversation-branch rollback plus a
  multi-hour gap: a marker written by one branch was read intact by another.
  The marker's own "UNVERIFIED" caveat is hereby closed by being read.
- `[FACT]` `touchscreen.tap` requires `has_touch=True` on the context;
  `blind_audit` never hit this because it uses a bare `new_page()` on a
  touch-enabled default. Mount signal is `#root.children.length>0`, not any
  `window.__mounted` flag.
- `[FACT]` `tools/tick.sh` (slides repo) measured live: stale-clone catch-up
  detected a real 70-line drift, prefetch dispatch 204, 2.13 s total.
- `[JUDGMENT]` "Blocked on X" entries deserve a second look at the
  architecture: P1's API-key blocker dissolved by moving the decider outside
  the tool. The ledger keeps the original claim; this line is the correction.

## 2026-08-30 · second Ralph pass (sibling branch, same conversation)

- The cross-branch handoff protocol worked as designed: marker →
  OPEN-PROBLEMS → Falsified → SANDBOX-FACTS stopped three duplicate builds
  (tick.sh, repo staging, packaging) before any code was touched.
- P1 stepper is deterministic across container instances (identical affordance
  set; screenshot RMS 0.93 with diff confined to the animated banner).
- P7 opened and closed in-session: sync now refuses src == dst. The bug was
  triggered, diagnosed, re-triggered twice by the fix procedure itself, then
  guarded — sequence discipline (patch → verify → only then touch fixtures)
  is the transferable lesson.

