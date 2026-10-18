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



---

## P-0a86 — `explore_step` acted before a page that fetches its data had rendered `CLOSED`

*ID by CONTRIBUTING rule 6: `P-` + first four hex of `sha1("explore_step acted before a page that fetches its data had rendered")`.*

Found 2026-09-29 by using the stepper on a page that is not a React artifact. `explore_step.py` waited for
`#root` to have children, which is true at DOMContentLoaded for a static shell; the speeds-kit GUI then fetched its
student list, so the first replayed click landed on an empty list. Symptom: a click "did nothing", screenshot identical
to the previous step, no error. The wrong first diagnosis was a slow server (measured 2 ms) — the fix was in the
stepper, not the page.

**Closed 2026-09-29:** navigate at DOMContentLoaded, then a *bounded* (5 s) best-effort wait for network idle plus a 250 ms settle;
readiness no longer assumes `#root`. The React path was re-run on a fixture artifact (unchanged output). A page that polls or
streams forever never reaches idle, so the wait may not be an error: checked on a page that fetches every 50 ms, which steps
normally after the 5 s bound. (First version used an unbounded `networkidle` and a review pointed out it would hang on exactly
those pages.)

## P-b279 — a scripted decider makes the impairment sweep runnable without an API key `OPEN`

*ID: `P-` + first four hex of `sha1("a scripted decider makes the impairment sweep runnable without an API key")`.*

P1 said the dose–response sweep is blocked on a paid API key. That was true of a *model* decider and false of the sweep:
a policy script that holds a goal and reads the rendered page is a decider, and it is free, deterministic per seed and about
2 s per trial. `checks/explore_run.py` runs it (README of `EXPLORE-SPEC.md`, "Implemented layer v1"). Status is `OPEN`, not `SPEC'D`, because part of it is now built. What stays open: a model
decider would bring common sense the scripts lack (a script that only knows how to find Q1c-ii cannot be surprised by a page it
was not written for), and working-memory limits are not modelled. Treat script-decider curves as a lower bound on how *findable*
a goal is for a reader who already knows what the app is; a first-time reader does worse.

## P-246d — in-page fragment links have no check that fails on a dead or hidden target `OPEN`

**The gap.** `blind_audit.py` is content-blind by design, so an `<a href="#x">` whose target does not exist, or exists with an empty box, passes every check in the kit. `region_shots.py`'s "anchors" are camera targets, not links. A dashboard artifact audited on 2026-09-06 (yulinl2/MetaProof `experiments/testbeds/T3-control/maintained/artifacts/`) carried a planted dead link that the audit did not see; a small Playwright check written there did.
**Design.** `checks/fragment_links.py`: sync, serve, open at 390×844, collect `a[href^="#"]`, for each target check existence, non-empty box after click, in-viewport after click. Content-aware, intention-less. Calibrated by `checks/test_fragment_links.py` on `checks/fixtures/fragment_links_planted.jsx` (one live, one dead, one inside a closed `<details>`, one `display:none`).
**Measured while calibrating (2026-09-26).** Chromium's fragment navigation opens a closed `<details>` ancestor, so a target folded in details is *live*; `display:none` is not undone. The fixture keeps both cases as the regression for that fact.
**Done-when.** The check is on `main`, the must-fire test is in CI, and `README.md`'s checks list names it.
**Hardened after review of PR #3 (2026-09-26).** The automated review found five real defects, all fixed with a test each: (1) a fixed 1.5 s sleep let a render error or a slow mount leave zero links and report PASS — now the check waits for the root to mount, collects page errors, and returns `ERROR`, or `EMPTY` (exit 3) when there is nothing to check (fixture `fragment_links_nolinks.jsx`); (2) the CI test skipped when Chromium failed to launch, turning a broken browser into a green job — now it fails under `CI=true`; (3) fragments were not percent-decoded (`#section%202` → id `section 2`); (4) the href was interpolated into a CSS selector, so a quote broke it — anchors are now selected by element handle (fixture `fragment_links_clean.jsx` covers both); (5) only the FAIL path was tested — a must-hold test on the clean fixture now asserts PASS with all three targets.
**Consumer.** `bin/emu` users; the T3 dashboard in MetaProof.


## Harness conventions misfire on pages that are not the harness (2026-10-02)

On TapGrade, `blind_audit`'s "row of exactly 2 buttons = a toggle" matched *Add deduction | Full credit* and tapped the
second; mechanically fine, semantically not a toggle. The checks still only assert mechanics, so nothing failed, but the
screenshot reader has to know which control was chosen. **Closes when** each interaction check records the matched
element's role, text length and geometry (not its text) next to its screenshot. Closed shadow roots stay invisible by
design; the report's `shadow_roots_walked` makes that visible.


## P-9d8b — operation chains cannot yet be captured from a driven session `OPEN`

*ID: `P-` + first four hex of `sha1("operation chains cannot yet be captured from a driven session")` (CONTRIBUTING rule 6).*

**The gap.** `checks/chain.py` reads chains that a person writes from a narration. The "later" half of #32, a chain captured from a
driven session, does not exist: `explore_run` and `explore_step` record decisions, not primitives with properties.
**Design.** `docs/OPERATION-CHAINS.md`, section "P-2a7c integration point": how a decision record becomes steps; what the runner can
measure without reading content and what the policy must declare; B is the run's own working-memory limit N. Related: P-2a7c
(decider-side working memory, PR #42).
**Cheapest first step.** The text backend (`checks/explore_text.py`): no browser, and its `mem_capacity` already bounds the decider's memory.
**Closes when** a scripted run writes a `source: captured` chain, `bin/emu chain check` reads it, the chain's `budget` equals the run's N,
and its RELOAD count equals the runner's own count of needed keys that were dropped. One test asserts all three.

## P-02be — chain verifiers read declared properties, so a chain can pass by omission `OPEN`

*ID: `P-` + first four hex of `sha1("chain verifiers read declared properties, so a chain can pass by omission")`.*

**The gap.** Each of the ten verifiers (`checks/chain_verifiers.py`) looks only at steps that declare the property it checks. A COMMIT
must say `everything_on_screen`; a list that is not marked list-showing is never asked where it came from; a refresh nobody recorded is
never checked. Silence means "nothing declared wrong". Each docstring says what that verifier cannot see; nothing yet tests a narration
against a measurement.
**Approximations, named.** The look-alike line (similarity 0.5) is a default, not a result of any experiment. `single_path` compares the
narrator's `intent` and `view` keys: two views under different keys are invisible. `idempotent` on a COMMIT removes two requirements and is
the narrator's claim. `held` is the narrator's list of what a person kept in mind.
**Evidence so far (2026-10-04).** An independent re-read of a narrated chain against its source (`hw1_correction_pass_transcribed.json`, see
`docs/OPERATION-CHAINS.md`, "HW1 twice") found the gap in both directions: stated properties left undeclared, so a verifier stayed silent (the
three presses of Scan, the `hw1` look-alike, the doubts about a blank result), and findings that follow only from a value the file had to supply
(a tap's feedback, what two refreshes kept, Apply's reversibility). The first kind is the gap above; the second is its mirror. This is a narration
checked against its narration, not against a measurement.
**Closes when** a captured chain (P-9d8b) and a narrated chain of the same task are compared property by property and the disagreements
are listed.

## P-67a1 — the chain load weights are ordinal and uncalibrated `OPEN`

*ID: `P-` + first four hex of `sha1("the chain load weights are ordinal and uncalibrated")`.*

**The gap.** `checks/chain_load.py` turns OPERATION-MODEL section 3 into one number with explicit weights (`WEIGHTS`). RELOAD = 6 and
RE-ORIENT = 3 follow from section 1's own decomposition; the others are ordinal judgement. None is measured. The number ranks chains of
one task; it is not minutes and has no threshold. The only gate in the layer is the budget flag.
**Closes when** the weights are checked against timed narrations or measured `explore_run` costs, and a test asserts the order they must
produce.

## P-2a7c — decider-side working memory: HOLD / KEYIFY / RELOAD for `explore_run` `OPEN`

EXPLORE-SPEC's implemented layer cannot model working-memory limits: its scripted policies re-read the page each step. A real
task (HW1 correction pass on a phone, 2026-10-03, narrated step by step) spent most of its cost in RELOAD (fetching a lost goal
from the chat) and RE-ORIENT (after refreshes), not in any single hard step. `docs/OPERATION-MODEL.md` gives the step anatomy,
the budget, and ten verifiers; issues #31–#40 split the work (chain format, load, verifiers, the HW1 fixture).
**Closes when** `explore_run` deciders hold at most N keys, RELOAD from a named source is a recorded step with its cost, the
sweep over N is reported next to the existing knobs, and the HW1 fixture's verifiers fire on the recorded chain.
## P-6e35 — the start block made this kit depend on a ledger it cannot assume `CLOSED`

The zero-hint block (4c88f9f, MetaProof #263) told every session to read MetaProof's ROOT-SEED first and had no path when
MetaProof was unreadable; a contributing session without access had to stall or proceed in violation (#44). For a
general kit in exploratory work, rigidity costs more than divergence. **Closed 2026-10-04 by the owner's decision**: this
repository stands on its own. CLAUDE.md and README point to README's own "Fresh session?" order; the SessionStart hook
prints that order (still zero-hint, now native); MetaProof is optional context. Divergence from the other repositories'
identical block is intended; sharing can come back later by choice.

**Update 2026-10-15 (the owner): fully standalone, not only while the kit is exploratory.** The kit is an infra thing apart from the content line, so CLAUDE.md no longer names MetaProof even as optional context. Its rule 1 ("Read MetaProof `ledgers/OWNER-POLICY.md` first") had survived the closure above and contradicted it: the file told a session both that nothing depends on MetaProof and to read MetaProof first. The rule is removed, with the sentence that called MetaProof's ledgers "useful when you can reach it", the history paragraph that pointed at a MetaSci issue, and the claim about what other lines' CLAUDE.md files point to (not checkable from this repository). CLAUDE.md now says what a session needs (the README's order, which the hook prints) and what the kit is. This supersedes "MetaProof is optional context" above; whether sharing a start block can come back later by choice (the last sentence above) is not decided here. The 2026-10-04 text is kept as written.

## P-dae1 — the kit's feedback is pull-only, so a session that never calls it is never told what it missed `OPEN`

*ID: `P-` + first four hex of `sha1("the kit's feedback is pull-only, so a session that never calls it is never told what it missed")` (CONTRIBUTING rule 6). Opened 2026-10-17 from the owner's message: recorded first, analysed after.*

**The observation, as given.** Looking at the loop figure of Gu, Kemeny, Yelin and Lukin, "Discovering state-of-the-art quantum circuits with large language models" (arXiv `…2367v1` [quant-ph], 15 Oct 2026; the ID prefix is cut off in the screenshot and was not looked up), the owner wrote: *"现在emu提供的feedback还太被动啦，agent不记得调用就被彻底遗忘，彻底陷入知识悖论。要是把evaluator+feedback这一块换成我们的“用户试用”action chain（再通过各种hook把iteration给首尾相接loop起来）岂不是就终于把它变成真正意义上的oracle-ish verifier了（这样才有可能绕过Oolong-Pro里面那个adverse pattern）"* — the kit's feedback is passive; an agent that does not remember to call it is never told, and cannot know to remember (the "knowledge paradox"); replace the figure's evaluator + feedback with this kit's user-trial action chain, close the iteration with hooks, and it becomes an oracle-ish verifier, which might get around the adverse pattern in Oolong-Pro. The owner also asked what tools make this visual style (answered outside the ledger; question 6 below is the part that touches the kit).

**Raw sources (the owner's three screenshots; not committed: third-party figures, and this kit's footprint is a stated property; first 16 hex of sha256).** `9e35348228c60402` loop figure, GIF 896×482, 114 frames, 168,481 B: Claude →(Edits)→ `solver.py` →(Circuit)→ Evaluator [Gate count, Qubit count] →(Feedback)→ Claude. `943663b82940bb17` PNG 1080×682, 103,291 B: seven panels, Toffoli count against peak qubits, prior work × against discovered ●. `1edd3e82335f5dc9` PNG, 472,368 B: the paper's first page; its abstract says LLMs "propose circuit designs and an independent evaluator verifies and scores them". Palette of the two figures, flat-fill sampling: neutrals lie within RGB distance 3.2 of the published `#faf9f5` and 1.4 of `#e8e6dc` (anthropics/skills, brand-guidelines); the accent `#cd7d5f` lies 15.6 from that skill's Orange `#d97757`.

**The idea, mapped.**

| The figure | The kit today | `checks/emu_loop.py` v0 |
|---|---|---|
| Claude edits `solver.py` | a session edits the artifact | the same; `--watch` globs |
| Circuit | the rendered page, or a recorded chain | a `bin/emu smoke` run; a chain file |
| Evaluator, independent | `bin/emu`, run only if the session remembers | run by hooks: PostToolUse after Write, Edit or Bash; Stop |
| Gate count, qubit count | exit code, one JSON line | vector `smoke_fail`, `chain_findings`, `chain_load`; dominance |
| Feedback → Claude | stdout of a command the session chose to run | `additionalContext`; a Stop refusal on stderr; both name the layers that did not run |
| keep the better candidates | none | append-only ledger, artifacts kept by hash, frontier, regression flag |

**Questions (open).**
1. Which pattern is "the adverse pattern"? `adverse` and `perverse` occur nowhere in this repository or in Oolong-Pro (grep, 2026-10-17, no match). Candidates in `Oolong-Pro/docs/01-hypotheses/registry.md`: H02, cheap verifiers that look high-coverage make performance look better than end-to-end quality (agents "infer too much from bells that do not ring"); H03, silence from an error-triggered alert is read as closure. Both are filed there as hypotheses with no completed trial. Which is meant, or neither?
2. "Oracle" in which sense? The same registry's H06 aims at "not replacing human judgment with a brittle yes/no oracle" and asks for appeals, provenance and calibration. EXPLORE-SPEC reports TRUE success as "ground truth from outside the page". A recorded chain's properties are declared by its narrator (P-02be). Which is the oracle here: ground truth from outside, declared properties, or a proxy with disclosed coverage?
3. Does a hook run where the work happens? SANDBOX-FACTS says "no hook system at all" (claude.ai chat containers, 2026-08). In a Claude Code cloud session (2026-10-17) hooks registered mid-session in `.claude/settings.local.json` produced no evaluation after two changes of a watched artifact (ledger: one `arm` record, no `eval`). Not known: whether a session that *starts* with the hooks fires them, and whether `additionalContext` reaches the model. The repository's own SessionStart banner was also not visible in that session's context. Update, same day: at the end of that turn a hook that is not this kit's, `~/.claude/stop-hook-git-check.sh`, ran, and its stderr with exit code 2 reached the model as "Stop hook feedback": the mechanism `emu_loop`'s Stop gate uses, observed working for that hook. The script also reads `stop_hook_active` from the payload. It is registered in no settings file found under `/etc/claude-code`, `/root/.claude` or `/home/user/.claude`, while this kit's project-level hooks (the checked-in SessionStart, the local PostToolUse and Stop) left no observable effect: the `emu_loop` ledger held no record after that turn. Why is not established; one candidate, untested, is that this harness registers its hooks itself and loads no project settings file.
4. Should the evaluator be hidden from the proposer? The paper's evaluator is independent; here the checker and the chains are readable files in the tree the agent edits.
5. Does the feedback's disclosure change behaviour? The v0 PASS message names the layers run and not run ("PASS means these layers found no defect"), which is the "explicit coverage disclosure" that Oolong-Pro's simulator cannot yet manipulate (`docs/04-evidence/tooling-audit-2026-10-14.md`, AUD-05). Untested whether it helps or becomes one more bell.
6. Should an aesthetic target (palette, type) be a verifier axis, or is that another tool's job?

**Doubts.**
- D1. A pass means "no defect found by these layers". The chain layer reads *declared* properties (P-02be), so a chain can pass by omission; the smoke layer is the one README `## Falsified` row 3 says must not present itself as a reader.
- D2. A scripted decider "knows too much" (P-b279); a model decider is paid and not reproducible (EXPLORE-SPEC, "Cost and placement"), the opposite of what a hook-driven gate wants.
- D3. The two chain fixtures are one recorded chain (`hw1_correction_pass.json`, narrated 2026-10-03) and one *designed* chain (`hw1_correction_pass_fixed.json`, 2026-10-04). Telling them apart shows the plumbing ranks a known-bad above a known-good, not that the loop improves any page.

**Concerns.**
- C1. Goodhart: an agent that can read the checker can tune to it. The ledger keeps every candidate, so a regression is visible afterwards; nothing prevents it.
- C2. A Stop gate can trap a session. v0 caps refusals per arming (`--max-rounds`, default 3; 0 observes and never blocks), counts them in the ledger, and fails open on any hook error.
- C3. Cost on every tool call: a disarmed hook measured 55.2 ms per call (mean of 20 runs, this container) for any session that installs the hooks; none for one that does not (`install` defaults to the uncommitted `.claude/settings.local.json`).
- C4. `checks/smoke.py:23` calls `p.chromium.launch` itself instead of `checks.browser.alaunch`, so it fails whenever pip's Playwright is newer than the container's Chromium (SANDBOX-FACTS, 2026-10-17). Not fixed here.
- C5. `install` left an untracked `.claude/settings.local.json`, and the harness's own Stop hook flags every untracked file and tells the session to commit it (`~/.claude/stop-hook-git-check.sh:32-37`): the first version of the loop generated work for a gate it did not know existed. `install` now adds the local file to `.git/info/exclude` (this clone only), and a test uses that hook's own predicate. `--shared` writes the tracked `.claude/settings.json` and needs no such step.

**What exists (prototype v0, branch `claude/emu-loop-prototype`).** `checks/emu_loop.py` (stdlib only): `arm`, `disarm`, `status`, `eval`, `install`, and the two hook handlers. Layers: `smoke` (`bin/emu smoke`; an infrastructure failure is NOT EVALUATED, not FAIL) and `chain` (`bin/emu chain check`, parsed into findings and load). A candidate is the artifact bytes plus the chain bytes; a layer that did not run makes the verdict NOT EVALUATED, which the Stop gate treats as not passing. Every feedback block lists the layers that ran, the ones that did not, and says the verdict is a proxy. `checks/test_emu_loop.py`: 16 tests, 0.73 s, no browser, **not wired into CI** (open: whether it should be). Measured here: `bin/emu chain check` on `hw1_correction_pass.json` exits 1 (26 findings, load 160.40 for its "expensive" chain plus 2.50 for "cheap"); on `..._fixed.json` exits 0 (0 findings, load 15.00). **Unit-tested, not observed end to end**: the hook did not run in the session that built it (question 3).

**Not done, and why.** The loop is not closed: the evaluator reads a chain somebody recorded, and capturing one from a driven run is P-9d8b; the goal-directed explore layer (P1) is not in the loop; no model decider. Nothing here claims the loop improves an artifact. This entry must not be read as licence for a fixed tap sequence to stand in for the user trial (EXPLORE-SPEC, "What must not happen to this spec"); the layer labels in every feedback block exist to stop that.

**Closes when** a session that never runs `bin/emu` itself still receives a verdict on an artifact it edited, computed from a chain *captured* from a driven run (P-9d8b), and its Stop is refused while that verdict fails; one test drives the hooks from a payload to a verdict on a rendered fixture and goes red when the hook wiring is removed. Related: P1, P2, P-02be, P-b279, P-9d8b, P-2a7c; Oolong-Pro H02, H03, H06.

**Update 2026-10-18 (a watch session, under the owner's instruction that day to merge the state of the art into main).** `checks/test_emu_loop.py` now runs in CI's `chains` job. No CI step ran it before: the same condition #64 fixed for two other test files (merged 2026-10-15). This settles "open: whether it should be" above for the unit tests only. Whether the hooks fire in a real session (question 3) is not changed by it, and neither is anything under "Not done, and why". The branch named in "What exists" is deleted when its pull request merges; commit `08b4637` is the prototype as written. Later the same day:
- **C4 is fixed on main** by #78. Every launch goes through `checks/browser.py`, which tries the headless shell first, and `checks/test_launch_sites.py` guards that in CI.
- **Review gaps.** Four Codex review rounds on #77 found nine real gaps in v0, and one more of the same kind was found alongside them. Each is fixed with a test that fails on the commit before it:
  - a watched artifact that disappears holds the stop;
  - a verdict is reused, compared, or taken as a baseline only under the same config (`config_of`) and at each candidate's newest verdict (`dominator`);
  - an arming is a ledger position (`since`), not a second;
  - the stop budget is counted in one place (`refusals`);
  - `install` keeps a hook command that shares a group with this one.
- `test_emu_loop.py` now has 23 tests.
