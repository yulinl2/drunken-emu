# Open problems

*v0.1.2 · 2026-08-31 · ledger, numbered, never renumbered*
*Provenance: build sessions 2026-08-22 → 08-31 (MetaProof Project).*

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

## P5 — no Zenodo DOI yet `SPEC'D`

Runbook: **`docs/ZENODO-RUNBOOK.md`** (written 2026-08-31 — it did not exist
before, which is why this entry sat in the human queue for three sessions
saying "enable Zenodo, then say the word" while giving nobody anything to
click). `CITATION.cff` is in place and carries the ORCID iD under `authors:`,
which Zenodo maps to DataCite `creators` — the field auto-update requires.

**Ordering constraint, now confidence A** (was B; raised 2026-08-31 after three
independent sources agreed): Zenodo archives only releases created *after* the
repository is enabled there. A release cut first mints no DOI and spends the
version number, because a repository cannot be attached to an existing Zenodo
record, no DOI can be reserved, and the DOI is unknowable before minting.

**Correction to this entry's earlier text.** It said to "authorise ORCID
auto-update" on Zenodo. That switch is not on Zenodo. Zenodo mints through
DataCite, so auto-update is enabled at <https://profiles.datacite.org/> →
Settings → ORCID Auto-Update. Anyone following the old wording would have
hunted for a control that does not exist.

**State checked 2026-08-31:** 0 tags, 0 releases, no Zenodo record under this
name. Nothing spent; `v0.1.0` is still free.

**Ready and waiting on the human:** part B of the runbook is one tag push plus
one API call, and `bin/apply_doi.sh <doi>` then writes the badge into README.md
and the `identifiers:` block into CITATION.cff idempotently (tested: applied
twice with different DOIs, exactly one of each remains, CFF still parses).

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

**Tested, not merely reasoned (2026-08-31):** the blocker above was inferred
from documentation. It has now been executed against the live repository with
the working token (`Contents` + `Actions` + `Workflows` + `Metadata`):

| Call | Result |
|---|---|
| `PUT /repos/yulinl2/drunken-emu/topics` | **403** `Resource not accessible by personal access token` |
| `PATCH /repos/yulinl2/drunken-emu` (homepage) | **403** |

Both endpoints are therefore confirmed closed to this permission set, not
assumed closed. Confidence on P6's blocker: **A**. The decision not to widen
the token stands, and this row exists so no future session re-spends the two
calls to find out.

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

---

## P8 — a live PAT sits in cleartext in `.git/config` `OPEN`

Found 2026-08-31 by inspecting a working tree that arrived from another
session. `git remote add origin https://x-access-token:<TOKEN>@github.com/...`
writes the token verbatim into `.git/config`, where it stays for the life of
the clone. Verified on this tree: the embedded token answered `GET /user` with
**200** and reports expiry `2026-09-29`.

Three ways it escapes, all of which have nearly happened in this project:

1. **Archiving the working directory.** `tar czf kit.tar .` from the repo root
   includes `.git/`. The kit was in fact shipped between sessions as a tar; had
   that tar been made one directory level up and after `git init`, the token
   would have travelled with it. `.gitignore` does not help — `.git/` is not a
   tracked path, it *is* the repository.
2. **Printing the remote.** `git remote -v` and `cat .git/config` both echo it
   in full. This is how it was found, which means it is also now in a
   conversation transcript.
3. **Any command that prints its own invocation** on error, since the URL is an
   argument.

**Mitigations, in order of preference.** (a) Keep the token out of the URL
entirely and pass it per-invocation:
`git -c http.extraheader="Authorization: Bearer $TOK" push ...`, reading `$TOK`
from a `600` file outside the repository. (b) If a token must be embedded,
treat the whole clone as a secret and never archive it. (c) Rotate on any
suspicion; fine-grained tokens are single-repo, so rotation is cheap.

Not closed here because the fix changes how every session sets up its remote,
and that convention belongs in `CONTRIBUTING.md` rather than being applied
silently by one session to one clone.
