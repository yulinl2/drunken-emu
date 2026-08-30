# Latest conclusions

*v0.1.0 · 2026-08-30 · maintained*
*Provenance: folded from the build sessions of 2026-08-22 → 08-30 (MetaProof
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
- `[FACT]` The linear *constant* spans 0.122–0.55 ms/node across three
  environments (4.5x). CI therefore asserts orderings and R², never constants
  — first CI run on a foreign runner passed 6/6 because of this choice.
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
