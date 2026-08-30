# Open problems

*v0.1.1 · 2026-08-30 · ledger, numbered, never renumbered*
*Provenance: build sessions 2026-08-22 → 08-30 (MetaProof Project).*

Read this before changing anything. Entries are numbered and never renumbered;
closed ones stay with a `CLOSED` marker and the evidence that closed them.

Status key: `OPEN` · `SPEC'D` (design settled, not built) · `CLOSED`

---

## P1 — `explore` mode does not exist `SPEC'D`

**The gap.** The original requirement for this kit was *long recursive click
chains, each step carrying an intention, formed from common sense and from what
is visible on the page* — an agent that behaves like a live person. What exists
is `checks/blind_audit.py`: 4 `touchscreen.tap` calls, one at a hardcoded pixel,
recursion depth 0, no variable carrying a result into a later decision.

**Why it looked acceptable for so long.** README principle 5 ("blind by
default") was used to justify the absence of goals. It never licensed that — it
licenses *content*-blindness only. See `## Falsified` row 3 in README.md. This
is the kit's most instructive bug: a capability gap defended by a correct
principle about something else.

**Design.** `docs/EXPLORE-SPEC.md`. The short version: not "an agent with
intentions" but "an agent with intentions **plus explicitly parameterised
impairment**", because a competent agent is the *wrong* proxy — it is patient,
remembers everything, and never gives up, so it would pass artifacts that real
readers fail.

**Blocked on.** A paid API key. `explore` needs a model call per step, so it can
never be the CI layer; `blind_audit` stays as the free deterministic gate.

---

## P2 — `blind_audit`'s self-description was wrong, its behaviour still is `OPEN`

Principle 5 has been rewritten to call `blind_audit` the *smoke layer* rather
than a reader model. That fixes the claim, not the code. Until P1 lands, this
kit cannot answer "can a reader accomplish anything here", only "does anything
visibly break".

Do not paper over this by adding more fixed taps. More taps in a fixed sequence
is still recursion depth 0.

---

## P3 — mount-cost constant is not portable `CLOSED`

Closed by measurement across three environments (0.55 / 0.17–0.21 / 0.122
ms/node — a 4.5x spread). Resolution: `checks/ci_claims.py` asserts orderings
and goodness-of-fit, never constants. Recorded in README `## Falsified` row 2.

Do not re-add a constant assertion. It will be red on day one somewhere.

---

## P4 — `[data-term]` coupling in the hit-area metric `OPEN`

`blind_audit.py`'s hit-area check assumes a `[data-term]` convention and
self-skips when absent. That is honest but narrow: artifacts not using that
convention get a silently reduced audit. Either generalise the affordance
detector or make the skip loud in the JSON output.

---

## P5 — no Zenodo DOI yet `OPEN`

Plan: tag `v0.1.0`, cut a GitHub Release, enable the repo in Zenodo, which mints
a DOI via DataCite. With ORCID auto-update authorised, the DOI then flows into
the author's ORCID record without manual entry. Nothing here is built yet; the
`CITATION.cff` is in place and already carries the ORCID iD.

---

## P6 — repo metadata is set by hand `OPEN`

Description / Website / Topics cannot be set with the current fine-grained PAT:
`PATCH /repos/{owner}/{repo}` needs `Administration: Read and write`, which
would also permit repo deletion. That trade was declined deliberately — do not
quietly widen the token to save two taps in a settings page.

Topics to add when convenient: `artifact-emulator` `headless-chromium`
`attention` `ui-audit` `react` `playwright`.
