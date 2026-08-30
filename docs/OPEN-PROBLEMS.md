# Open problems

*v0.1.2 · 2026-08-30 · ledger, numbered, never renumbered*
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

**Blocked on.** A paid API key — *for the automated sweep only.* The blocker
was dissolved for interactive use on 2026-08-30 by inverting the architecture:
`checks/explore_step.py` is a **stateless stepper** (replay trace → apply one
action → observe under impairment flags) and the **calling session is the
decider**. No API call, no daemon, deterministic replay ≈0.5 s/step overhead.
Observation-side impairments (`--salience`, `--impulsivity`) live in the
stepper; decider-side ones (working-memory N, distractibility p, patience k)
are the session's contract, stated in EXPLORE-SPEC's implemented-layer note.
Demonstrated end-to-end: salience-trap fixture, 3-step trace, one deliberate
hijack, goal reached. Dose–response sweeps still need an API decider; P1 stays
open for that half only.

**Reproducibility (2026-08-30, second container instance).** The recorded
3-action trace replays deterministically against the preserved fixture:
affordance set identical (salience trap / settings / `units: mi`), final
screenshot RMS 0.93 vs the original run (diff bbox confined to the animated
banner — phase, not content), 1.8 s for launch + 3 actions + shot — consistent
with the ~0.5 s/step claim.


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

## P4 — `[data-term]` coupling in the hit-area metric `CLOSED`

`blind_audit.py`'s hit-area check assumes a `[data-term]` convention and
self-skips when absent. That is honest but narrow: artifacts not using that
convention get a silently reduced audit. Either generalise the affordance
detector or make the skip loud in the JSON output.

**Closed 2026-08-30** by the loud-skip route: `blind_audit` JSON now carries
`term_hit_status: "checked" | "SKIPPED: no [data-term] convention…"`. Verified
on a data-term-free fixture (status string present, other checks unaffected).
Generalising the detector remains possible future work but the silent-degrade
hazard is gone.

---

## P5 — no Zenodo DOI yet `OPEN`

Plan: tag `v0.1.0`, cut a GitHub Release, enable the repo in Zenodo, which mints
a DOI via DataCite. With ORCID auto-update authorised, the DOI then flows into
the author's ORCID record without manual entry. Nothing here is built yet; the
`CITATION.cff` is in place and already carries the ORCID iD.

**Ordering constraint (added 2026-08-30, confidence B — Zenodo webhook
behaviour from documentation, not yet exercised here):** Zenodo archives only
releases created *after* the repo is enabled on zenodo.org; a release cut first
mints no DOI and burns the version number. Runbook: (1) human — zenodo.org →
GitHub → enable drunken-emu, authorise ORCID auto-update; (2) session — push
tag `v0.1.0` + create the GitHub Release via API (`Contents: RW` suffices);
(3) verify the DOI, add badge to README and `doi:` to CITATION.cff. Step 2 is
ready and waiting on step 1.


---

## P6 — repo metadata is set by hand `OPEN`

Description / Website / Topics cannot be set with the current fine-grained PAT:
`PATCH /repos/{owner}/{repo}` needs `Administration: Read and write`, which
would also permit repo deletion. That trade was declined deliberately — do not
quietly widen the token to save two taps in a settings page.

Topics to add when convenient: `artifact-emulator` `headless-chromium`
`attention` `ui-audit` `react` `playwright`.

**Partial (2026-08-30):** `description` was set by hand (🦤 chosen — the
author's call, overruling a 🪿 recommendation). `homepage` and `topics` remain
unset; the topic list above still applies.

---

## P7 — `sync_artifact` double-processes its own output `CLOSED`

Found 2026-08-30 by doing it: a session passed `harness/app.jsx` (a synced
*output*) back through `bin/emu step`, which unconditionally re-syncs. Each
pass appends another hook rebind and another mount call; duplicate `const`
declarations are a SyntaxError, so React never mounts and every check dies at
`wait_for_function` timeout with no visible cause. It then recurred twice more
*during the fix attempt* (an assert aborted mid-sequence before the restore
step; a guard test re-ran the corrupting sync) — the failure compounds
silently and invites itself back.

**Closed 2026-08-30:** `main()` refuses `realpath(src) == realpath(dst)`
(exit 2, named reason). Verified: guard fires on self-input; distinct-path
sync is byte-identical across repeated runs on the same input. Full
idempotence (safe re-sync of any already-synced file) remains future work;
this guard removes only the observed footgun.
