# Open problems

*v0.1.4 · 2026-08-31 · ledger, numbered, never renumbered*
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

**Convention landed 2026-08-31** as `CONTRIBUTING.md` rule 7: move history with
`git bundle`, never with a tar of a working tree. Credential-free bundles of
both repositories now sit in `/mnt/user-data/outputs/bundles/`, and a clone from
one was checked for `github_pat_`, `x-access-token` and `olp_` in the restored
`.git/config` — clean, on a second independent sampling.

Still `OPEN`, and the remaining half is the larger one: the *existing* clones
still carry the token in their remote URL, and no session has switched to
`git -c http.extraheader=...`. The rule tells new clones what to do; it does
nothing about the ones already on disk.

---

## P9 — this ledger's numbering cannot survive parallel sessions `OPEN`

Numbers here are allocated max-seen-plus-one, which assumes a single writer.
This project has not had a single writer since 2026-08-30: on 08-31 two sessions
worked the same repository within one hour, and a third arrived holding a clone
three commits stale. Two sessions that each open a problem allocate the same
integer, and `CONTRIBUTING.md` rule 4 forbids rewriting `main`, so the collision
is permanent — two different P9s, both published, neither withdrawable.

**This is not a new discovery.** The same failure is recorded as `NEED-0011` in
the sibling metascience loop, where region-B ledger IDs are also sequential
integers and two parallel retry branches each wrote a different `COR-0007` into
an append-only file. That loop found it first; this repository re-derived the
hazard from scratch because nothing connects the two ledgers. The cost of the
missing link is one rediscovery, which is cheap; the next one may not be.

**Convention landed 2026-08-31** as `CONTRIBUTING.md` rule 6: content-derived
identifiers, `P-<first 4 hex of sha1(title)>`, allocated without reading any
other entry and therefore collision-free without coordination. `P1`–`P10` keep
their names forever.

The scheme is now **in use**: the entry below this one is `P-9cef`, the first
allocated under it. Two sessions writing the same title would produce the same
id and collide harmlessly on identical content; two writing different titles
cannot collide at all.

**Left deliberately as `P9`** under the old scheme, so the ledger carries one
instance of the hazard it describes.

---

## P10 — organisational conventions proven in sibling loops are not adopted here `OPEN`

A search of this project's other Ralph loops on 2026-08-31 found machinery that
neither this repository nor the Overleaf sync repository uses. Recorded here so
the comparison is not re-run:

| Convention | Where it is in service | State here |
|---|---|---|
| Numeric filename prefixes fixing read order (`00_INDEX_dir-tree`, `01_OPEN-PROBLEMS`, `02_LATEST-CONCLUSIONS`, `03_REFERENCE-LEDGER`, `05_ERRATA_*`) | CORAL loop | absent — read order is prose in the README, so it is advisory rather than structural |
| `00-HANDOFF-README.md` as a named entry point distinct from the landing README | HAN compendium | absent |
| **md5 identity table** in the handoff document, verified on wake against the files it names | HAN compendium | absent — nothing here detects a file that was replaced rather than edited |
| Three-region state: A immutable md5-pinned seed · B append-only data · C replaceable numbered rules carrying their own derivation and revocation records | metascience loop | absent — `docs/` is flat, and mutability is not marked |
| `MANIFEST` checksums · `LINEAGE.txt` · `loop-history.bundle` for transport across container identity | metascience loop | absent; `git bundle` in particular crosses the boundary that a tar of a working tree crosses unsafely (see P8) |
| Step-zero read cost *measured*, not just prescribed (~9,450 words ≈ 13% of corpus) | metascience loop | absent — the README states a reading order and never says what it costs |
| `NEED-####` and `COR-####` ledgers separate from the problem ledger | metascience loop | absent — everything is a `P` |

Not adopted wholesale: this repository is a public tool with outside readers,
and the heavier apparatus was built for a private corpus with a different
audience. The two worth taking regardless are the **md5 identity table** (P8
showed working trees arrive from elsewhere with unknown provenance) and the
**git bundle** transport (it carries history and refuses to carry `.git/config`
credentials, which is exactly the P8 hazard).

---

## P-9cef — a blocked entry has no way to notice its blocker clearing `OPEN`

*First entry under the content-derived scheme (`CONTRIBUTING.md` rule 6):
`P-` + first four hex of `sha1("blocked-on entries have no mechanism to notice
the blocker clearing")`. Allocated without reading any other entry.*

Twice now, an entry has sat in a blocked state after the block was gone.

| Entry | Said it was waiting for | What had actually happened |
|---|---|---|
| P5 | "enable Zenodo, then say the word" | sat three sessions with no instructions written; fixed by `docs/ZENODO-RUNBOOK.md` |
| P8, P9 | "the convention belongs in `CONTRIBUTING.md`" | rules 6 and 7 were written by another session; both entries still read as unwritten when re-read on 08-31 |

The shape is the same both times, and it is specific to a many-session ledger:
the session that clears a blocker is rarely the session that recorded it, and
nothing links the two. In a single-author repository the author remembers; here
memory *is* the ledger, so an unlinked blocker is a permanent one.

**Not a documentation problem.** Both entries were accurate when written and
neither author was careless. What is missing is a mechanical re-read trigger.

**Fix, partially applied.** `bin/blocker_check.py` lists every `OPEN` or
`SPEC'D` entry that names a tracked file, together with whether that file has
changed more recently than the ledger. It cannot decide whether the block is
genuinely cleared — that needs reading — but it turns "remember to re-check
everything" into a short list, which is the part a session can actually do.
Advisory by design: a hard CI failure would make every edit to `CONTRIBUTING.md`
red, which trains people to ignore it.

## P-8c1e — the explore layer had no test that fails when it is absent `OPEN`

*ID allocated by CONTRIBUTING rule 6: `P-` + first four hex of `sha1("the explore layer had no test that fails when it is absent")`.*

**The gap.** P1 explains *why* the explore layer stayed unbuilt across sessions: its requirement
lived in prose, and each fresh session re-read it as the smoke layer. But the ledger recorded
the cause without installing the mechanism that would have prevented it: nothing in CI turned
red while the layer was missing. A rule that is not a failing test is a wish (the MetaProof
case-study phrase: *will does not bind; mechanism binds*).

**Seed installed 2026-09-23.** `checks/explore_text.py` is the explore loop's harness mechanics
on a text page — a Markdown heading tree stands in for the rendered artifact; a window of `w`
lines for the screen; headings, links and section references parsed from the view for
affordances; a bounded, decaying memory; impairment knobs (`p_drop`, `eps_misnav`,
`mem_capacity`); a pluggable policy. `checks/test_explore_text.py` asserts the three parts of
the original requirement (recursion depth ≥ 3; a decision at step k+2 or later referencing a
note from step k; every `open` drawn from visible affordances) with a *scripted* policy, and
asserts that a stateless tapper fails. No model call; runs in CI in under a second (`claims.yml`
job `explore-seed`). Its role and the bootstrap ladder it belongs to are in the MetaProof
proposal §7 (https://github.com/yulinl2/MetaProof/pull/21 ).

**What this does not close.** P1's browser half: the same loop over `checks/explore_step.py`
with a decider, and the dose–response sweep that needs an API decider. The text backend is
the cheapest place to make the loop's *mechanics* fail loudly; the browser backend inherits the
loop and the test shape, not the fixture.

**Closes when** the browser backend passes an equivalent of `test_explore_text.py` (same three
assertions, a rendered fixture) in CI.

