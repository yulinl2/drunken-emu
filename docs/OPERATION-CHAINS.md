# Operation chains — what a task costs a person, as a file you can check

*v0.1.0 · 2026-10-04 · built · issues #31–#40 · model: `docs/OPERATION-MODEL.md`*

## The point

- `docs/OPERATION-MODEL.md` says what a person does, step by step, and what it costs.
- This layer makes that checkable.
- Record a task as a **chain file** (JSON).
- `bin/emu chain check` returns the cost and the findings, each with its step number.
- No browser, no model call. Python standard library only. The tests run in about 1 s.

## Run it

```
bin/emu chain check CHAIN.json [CHAIN2.json ...] [--budget B] [--json] [--chain ID] [--lookalike X]
```

| Exit | Meaning |
|---|---|
| `0` | no findings in any chain checked |
| `1` | at least one finding |
| `2` | the file is not a valid chain, or the usage is wrong, or the checker itself crashed (never exit 1: that means findings only); every problem is listed, each with its step number |

| Option | Does |
|---|---|
| `--budget B` | working-memory slots B for every chain checked. Default: the chain's own `budget`, else 3 |
| `--json` | one JSON document on stdout instead of the report |
| `--chain ID` | check only this chain id, in whichever input file has it (repeatable). An id is unknown only when no file has it; a file with none of the named chains is skipped |
| `--lookalike X` | similarity (0..1) from which `confusables` count as look-alikes. Default 0.5 |

Try it:

```
bin/emu chain check checks/fixtures/chains/hw1_correction_pass.json         # exit 1: the recorded chain
bin/emu chain check checks/fixtures/chains/hw1_correction_pass_fixed.json   # exit 0
python3 -m pytest -q checks/test_chain.py                                   # CI job `chains`
```

## What is in the box

| File | Role | Issue |
|---|---|---|
| `checks/chain.py` | the format: load, validate, normalise | #32 |
| `checks/chain_load.py` | the load and the working-memory budget | #33 |
| `checks/chain_verifiers.py` | the ten verifiers | #33–#39, §5.10 |
| `checks/chain_check.py` | the CLI behind `bin/emu chain check` | #31 |
| `checks/fixtures/chains/` | the HW1 chains (recorded, fixed), the TapGrade 0.6.6 chains (what was built) and the worked example | #40 |
| `checks/test_chain.py` | must-fire, must-hold, mutation controls | all |

## The format

JSON is canonical. One file holds one chain, or several under `chains`.

```json
{ "provenance": {"source": "narrated", "date": "2026-10-03", "who": "me"},
  "steps": [ {"op": "ANCHOR", "anchor": "edge", "target": "the menu button, top right"},
             "READ the first line" ] }
```

- A step is an object, or a string `"OP free text"` (shorthand for `{"op": OP, "target": text}`).
- YAML works only if PyYAML happens to import. It is never required.
- `format` is optional. If present it must be `"emu-chain/1"`.

### File and chain keys

| Key | Where | Meaning |
|---|---|---|
| `chains` | file | several chains; each needs an `id` |
| `steps` | chain | the steps; non-empty |
| `id` | chain | short name; required when a file holds several |
| `provenance` | file or chain | `source` (`narrated` · `designed` · `captured`), `date` (YYYY-MM-DD), `who` (a role is enough), optional `note`. A chain's keys override the file's, key by key |
| `budget` | file or chain | working-memory slots B for this chain |
| `task`, `setup`, `notes` | chain | free text for humans |

### Step keys (any step)

| Key | Values | Default | Means (OPERATION-MODEL §2) |
|---|---|---|---|
| `op` | the 16 ops below | required | what the person did |
| `target`, `note` | free text | empty | for humans. **No verifier can read them** |
| `anchor` | `edge` · `fixed-position` · `unique-visual` · `text-keyword` · `none` | `none` | how the target was found. An ANCHOR step requires one of the first three |
| `confusables` | `[count, similarity]` | no look-alikes | how many look-alikes, how alike (0..1). With count ≥ 1 the similarity is required |
| `need` | whole number | per op (table below) | slots the step itself needs |
| `held` | list of labels | **inherited from the step before** (first step: empty) | items in memory across the step, one slot each. `[]` clears |
| `reading` | `none` · `coarse` · `fine` | per op | how the person read |
| `amount` | number | 1 (0 if `reading` is none) | items read |
| `feedback` | `immediate` · `delayed` · `none` | `immediate` | what the system answered |
| `reversibility` | `idempotent` · `reversible` · `irreversible` | `idempotent` (COMMIT: required) | cost of an error |
| `interruption` | subset of `position`, `goal`, `partial` | none | what an app switch or refresh **at this step** loses |
| `times` | whole number ≥ 1 | 1 | the step was done n times in a row ("loop ×3"): n consecutive copies of it in every count. A repeated body is each of its steps with the same `times` |
| `intent`, `view` | short keys | none | the job this step performs, and the view it happens in. `intent` needs `view` |
| `origin_stated`, `exclusions_stated` | true / false | absent | the step shows a list or a prompt. Give both or neither |
| `boundary_visible` | true / false | absent | the step reads block-structured text |

### Keys that belong to one op

| Op | Key | Values | Required? |
|---|---|---|---|
| ANCHOR | `anchor` | `edge` · `fixed-position` · `unique-visual` | yes |
| DISCRIMINATE | `confusables` | `[count ≥ 1, similarity]` | yes |
| HOLD · KEYIFY · RELOAD | `held` | the list **after** the step; it must differ from before | yes |
| RELOAD | `source` | where the lost goal is fetched from (`"chat"`, `"notes"`, `"task text"`) | yes |
| REFRESH | `restores` | subset of `position`, `goal`, `partial` | yes |
| RE-ORIENT · NAVIGATE | `restores` | same | no |
| WAIT | `progress_visible`, `view_stable` | true / false | yes |
| WAIT | `partial_result_says_left` | true / false; absent = this wait yields no partial result | no |
| COMMIT | `preview_before`, `everything_on_screen` | true / false | yes |
| COMMIT | `verify_after` | `none` · `consistency` · `correctness` | yes |
| COMMIT | `reversibility` | `idempotent` · `reversible` · `irreversible` | yes |
| ENUMERATE | `set_visibly_complete` | true / false | no (false) |
| ENUMERATE | `pages` | whole number ≥ 1 | no (1) |
| VERIFY | `kind` | `consistency` · `correctness` | yes |

A key on the wrong op is an error, not a no-op.

### What the required keys mean

Answer each as the person saw it, not as the system was designed.

| Key | Means | Read by |
|---|---|---|
| COMMIT `preview_before` | before committing, the person saw what each row would become | `colocation` |
| COMMIT `everything_on_screen` | everything the decision depends on was on the screen at that moment | `colocation` |
| COMMIT `verify_after` | what the system did afterwards: `none`; `consistency` (checked the target against its own records); `correctness` (re-read the target and reported against the intent) | `commit_correctness` |
| WAIT `progress_visible` | the screen showed that something was happening, and how far | `progress` |
| WAIT `view_stable` | the view did not move during the wait (no jump to the top) | `progress` |
| WAIT `partial_result_says_left` | a partial result says what is left, and why the rest failed | `progress` |
| REFRESH `restores` | what is **still there after** the refresh: `position`, `goal`, `partial`. The verifier flags what is missing | `interruption` |
| `interruption` (any step) | what an app switch or refresh **at this step** would take away. `restores` is what survives, `interruption` is what is lost | `interruption` |
| ENUMERATE `set_visibly_complete` | the person could tell the set was complete without paging (a count, "all shown") | `candidate_set` |
| ENUMERATE `pages` | how many screens were paged through | `candidate_set` |
| VERIFY `kind` | `consistency`: A matches B. `correctness`: A matches what was intended | `commit_correctness` |
| RELOAD `source` | where the lost goal was fetched from | `memory_budget` |

**SCAN or ENUMERATE?** A SCAN coarse-reads items already in view to find a keyword. An ENUMERATE makes sure the whole set has been seen: paging, scrolling, checking the seams between screens. Scrolling to find one item is a SCAN per screen. Scrolling to be sure nothing is missing is an ENUMERATE with `pages`.

**Labels are compared as written.** `intent`, `view`, `held` labels and RELOAD `source` are compared after trimming the spaces at both ends: `re-sync ` and `re-sync` are one view, `Re-sync` and `re-sync` are two. YAML reads an unquoted `2026-10-03` as a date: that works too.

### The sixteen ops, and what a plain step costs

The 15 primitives of OPERATION-MODEL §1, plus `TAP`. `TAP` is the physical act on a target an earlier step chose. §4 writes it in both chains, so it is here: it costs nothing.

| Op | `need` | `reading` | Note |
|---|---|---|---|
| `ANCHOR` | 0 | none | found without reading |
| `SCAN` | 1 | coarse | set `amount` to the items scanned |
| `READ` | 1 | fine | |
| `ENUMERATE` | 1 | coarse | paging through a set |
| `DISCRIMINATE` | look-alikes + 1 | fine | |
| `HOLD` · `KEYIFY` · `RELOAD` | 1 | none | each changes `held` |
| `NAVIGATE` | 0 | none | |
| `RE-ORIENT` | 1 | coarse | `REORIENT` is accepted |
| `INFER` | 1 | none | |
| `WAIT` · `REFRESH` | 0 | none | |
| `COMMIT` | 1 | none | |
| `VERIFY` | 1 | coarse | set `reading: fine` for a check by hand |
| `TAP` | 0 | none | zero cost |

A RELOAD is itself a chain (§1). Write it flat: the `RELOAD` step, then the ANCHOR, READ, … KEYIFY steps that follow.

### What the loader refuses (every one is a test)

- an unknown op, key or value (with a "did you mean");
- a missing required key;
- a key on the wrong op;
- an ANCHOR found by reading (make it a SCAN);
- a DISCRIMINATE with no look-alike;
- a HOLD, KEYIFY or RELOAD that changes nothing;
- `intent` without `view`; one of `origin_stated` / `exclusions_stated` without the other;
- a bad date, an unknown `source`, a repeated chain `id`, a duplicate JSON key, `NaN`.

All problems come back **in one pass**, each naming its step. Fix them together.

### Free text is walled off

- Free text: `target`, `note`, `task`, `setup`, `notes`, provenance `who` and `note`.
- After loading it lives under `text`. `chain.blind()` removes it.
- `run_chain` hands the verifiers and the load the blind chain. They cannot read it.
- Three kinds of label stay: `intent` / `view` keys, `held` labels, RELOAD `source`. They are compared or counted, never interpreted.
- `test_chain.py` proves it twice: a tripwire where the text lives, and a scramble of every free-text field that must change nothing (findings, messages and load).

## Write a chain from a narration in 5 minutes

1. Open `checks/fixtures/chains/worked_example.json` and copy it. Change `provenance`.
2. One line per thing the person did. Pick the op from the table. Put the narration's words in `target`.
3. Add what the narration says. "Nine menu items" → `amount: 9`. "Almost the same name" → `confusables: [1, 0.9]`. "Nothing moved" → `progress_visible: false`.
4. Memory: write `held` at the step where the person starts keeping something in mind. Write it again only when it changes.
5. Steps that carry a verdict (COMMIT, WAIT, REFRESH, VERIFY, RELOAD) have required keys. The loader names the one you forgot; "What the required keys mean" says what each asks.
6. Run `bin/emu chain check FILE`. Fix by step number.
7. Guess amounts and similarities. Write that in `provenance.note`. They are estimates, not measurements.

### Worked example

The narration (made up):

> I opened my bank's app for last month's statement. I tapped the menu, top left. I scanned nine items for "Statements"; "Statement settings" sits right under it. I tapped Statements, scrolled years then months, tapped last month. The page said "Loading" and nothing moved. I switched to messages to answer someone and came back: the app was on the home screen again. I had to work out where I was.

The chain (`checks/fixtures/chains/worked_example.json`):

<!-- worked-example:json -->
```json
{
  "provenance": {"source": "narrated", "date": "2026-10-04", "who": "made up for docs/OPERATION-CHAINS.md"},
  "task": "Get last month's statement in a banking app (a made-up narration)",
  "steps": [
    {"op": "NAVIGATE", "held": ["goal: last month's statement"], "target": "open the app"},
    {"op": "ANCHOR", "anchor": "edge", "target": "the menu button, top left"},
    {"op": "SCAN", "amount": 9, "confusables": [1, 0.9], "anchor": "text-keyword", "target": "nine menu items, looking for 'Statements'; 'Statement settings' is right under it"},
    "TAP Statements",
    {"op": "SCAN", "amount": 14, "target": "years, then months"},
    "TAP last month",
    {"op": "WAIT", "progress_visible": false, "view_stable": true, "target": "'Loading', nothing moves"},
    {"op": "NAVIGATE", "restores": [], "target": "switch to messages, come back: the app is on the home screen again"},
    {"op": "RE-ORIENT", "amount": 6, "target": "where am I, what was I doing"}
  ]
}
```

The report (`bin/emu chain check checks/fixtures/chains/worked_example.json`, exit 1):

<!-- worked-example:output -->
```
checks/fixtures/chains/worked_example.json
  chain-1  Get last month's statement in a banking app (a made-up narration)  [narrated 2026-10-04]
    9 steps · B 3 · peak 2 slot(s) (held 1) · RELOAD 0 · RE-ORIENT 1
    load 19.25 = reading 7.25 + slot-steps 9 + RELOAD 0 + RE-ORIENT 3 + discriminate 0.00 + loops 0
    3 finding(s)
      step 3   SCAN         anchoring          SCAN chooses among 1 look-alike(s) (similarity 0.90) by reading only (anchor: text-keyword); give the target an edge, fixed-position or unique-visual anchor, or remove the look-alikes  [nine menu items, looking for 'Statements'; 'Statement set...]
      step 7   WAIT         progress           no visible progress during the wait  ['Loading', nothing moves]
      step 8   NAVIGATE     interruption       after NAVIGATE not restored: position, goal, partial  [switch to messages, come back: the app is on the home scr...]

FAIL  3 finding(s) in 1 chain(s)
```

How to read it:

- Step 3: two near-identical names, found by reading a keyword. Anchor it, or rename one.
- Step 7: a wait with no progress. The person cannot tell stuck from slow.
- Step 8: leaving and coming back lost position, goal and partial work.
- Step 2 is silent: found at an edge, no reading. Step 5 is silent: a SCAN over unlike items is not a finding.

## The load

OPERATION-MODEL §3 gives the formula. `checks/chain_load.py` gives each term a number and an explicit weight.

> chain load ≈ reading + Σ(slots × steps held) + RELOADs + RE-ORIENTs + DISCRIMINATEs × similarity + WAIT/VERIFY loops

| Term | Counted | Weight (`WEIGHTS`) | Why that weight |
|---|---|---|---|
| reading | fine-read items; coarse-read items | `read_fine` 1.0; `read_coarse` 0.25 | §1 calls a SCAN shallow |
| slot-steps | items held across each step, × `times` | `slot_step` 1.0 | ordinal |
| RELOAD | RELOAD steps × `times` | `reload` 6.0 | §1: a RELOAD is itself a chain of five steps, and it interrupts the task |
| RE-ORIENT | RE-ORIENT steps × `times` | `reorient` 3.0 | §1: ENUMERATE of the local options, "often" plus a RELOAD: half a RELOAD |
| discriminate | Σ similarity of DISCRIMINATE steps × `times` | `discriminate` 3.0 | ordinal |
| loops | REFRESH steps directly after a WAIT, a VERIFY, or a REFRESH that was itself one, × `times` | `loop` 2.0 | ordinal |

- **The weights are not measured.** They make the order the source narration reports come out: RELOAD and RE-ORIENT loops dominate, not any single hard step.
- Use the number to compare chains of the **same task**. Never as a threshold, a score or minutes.
- The report shows the components next to the one number.
- **Length is reported, never optimised.** `steps` is printed beside the load and is not a term of it. Fifty steps that read nothing and hold nothing add 0 (tested).

The budget:

- A step's working set is `need` (what it juggles itself) + the items in `held`.
- B is the number of slots. Default 3. Precedence: `--budget`, then the chain's own `budget`, then 3.
- `peak_slots` is the largest working set. `over_budget_steps` lists the steps above B.
- Past B something falls out, and the chain gains a RELOAD (§3).

The HW1 chains, measured by `bin/emu chain check` on 2026-10-04:

| Chain | Steps | Load | Peak slots | RELOAD | RE-ORIENT | Findings |
|---|---|---|---|---|---|---|
| `cheap` | 6 | 2.50 | 1 | 0 | 0 | 0 |
| `fixed` | 10 | 15.00 | 2 | 0 | 0 | 0 |
| `expensive` | 34 | 160.40 | 5 | 1 | 6 | 26 |

`test_chain.py` asserts the order (cheap < fixed < expensive) and the exact `cheap` and `expensive` numbers (a transcription). `fixed` is the designed target and stays as it is; the flow as built is measured in "TapGrade 0.6.6: the chains the code implements" below.

## The ten verifiers

Each is a content-blind function over the blind chain. It returns `{verifier, step, message}`, at most one per step. A verifier looks only at steps that **declare** the property it checks. Silence means "nothing declared wrong", never "nothing wrong". Each docstring in `checks/chain_verifiers.py` says what it cannot see.

| Verifier | §5 | Issue | Cannot see |
|---|---|---|---|
| `anchoring` | 5.1 | #38 | whether the declared anchor is true; look-alikes nobody counted; whether 0.5 is the right line |
| `memory_budget` | 5.2 | #33 | what the person really held (`held` is the narrator's list); B is a parameter, not a measurement; whether a RELOAD was avoidable |
| `candidate_set` | 5.3 | #38 | a set nobody tried to enumerate; a "complete" claim the page makes falsely |
| `interruption` | 5.4 | #34 | a refresh or app switch nobody recorded; whether a "restored" view is the same view |
| `colocation` | 5.5 | #35 | which information a decision depends on (`everything_on_screen` is a yes or no); an `idempotent` label is a claim |
| `progress` | 5.6 | #36 | whether a visible spinner is honest; how long a wait is |
| `causal` | 5.7 | #37 | whether an inference is actually wrong; a list nobody marked as list-showing |
| `single_path` | 5.8 | #39 | two views doing one job under different `intent` keys; whether two `view` keys are really different views |
| `commit_correctness` | 5.9 | #39 | whether a reported "correct" is correct; whether the later VERIFY is about this commit |
| `separators` | 5.10 | #31 (no sub-issue) | text nobody marked block-structured; what the right separator would be |

| Verifier | Flags a step when | Seen in the source |
|---|---|---|
| `anchoring` | `confusables` count ≥ 1 and similarity ≥ 0.5, and `anchor` is `text-keyword` or `none` | paging a Files folder for one of 12 look-alike names; guessing which bottom tab updates Canvas (#38) |
| `memory_budget` | `need` + `held` > B, or the step is a RELOAD | HOLD overflows, the goal falls out, the person fetches it from the chat (§4) |
| `candidate_set` | ENUMERATE with `set_visibly_complete` not true | checking the seams between screens (#38) |
| `interruption` | `restores` lacks position, goal or partial; or `interruption` is non-empty | Apply jumped the view to the top; a refresh lost the place in the list (#34) |
| `colocation` | COMMIT with `everything_on_screen` false, or `preview_before` false (unless `idempotent`) | "summary comment" rows could not be opened: the review before Apply was a formality (#35) |
| `progress` | WAIT with `progress_visible`, `view_stable` or `partial_result_says_left` false; or any step with `feedback: none` | 66 changes, Apply "stuck", 42 left after a refresh; "Removed 18 of 54" without saying why 36 failed (#36) |
| `causal` | a list or prompt step with `origin_stated` or `exclusions_stated` false | a list of changes appeared before the corrections were loaded: the person inferred they were in (#37) |
| `single_path` | one `intent` served by two or more distinct `view`s (one finding per intent, at the second view) | corrections vs Re-sync (#39) |
| `commit_correctness` | COMMIT whose `verify_after` is below correctness (idempotent: consistency is enough), or no later VERIFY of that kind | the system said everything matches; the person verified by hand (#39, §4) |
| `separators` | `boundary_visible` false | a key vs the grader's note: narrow to the paragraph, then the sentence (§5.10) |

`reversibility` sets how strict two verifiers are (§1: irreversibility multiplies the cost of an error). An `idempotent` COMMIT needs no preview and may stop at consistency. That label is the narrator's claim, not a check.

## The fixtures

| Chain | File | Steps | Result |
|---|---|---|---|
| `cheap` | `hw1_correction_pass.json` | 6 | no findings |
| `expensive` | `hw1_correction_pass.json` | 34 | all ten verifiers fire (26 findings) |
| `fixed` | `hw1_correction_pass_fixed.json` | 10 | no findings; peak 2 slots; no RELOAD; no RE-ORIENT |
| `tapgrade-0.6.6` | `tapgrade_0_6_6.json` | 10 | 1 finding: step 7, Apply (the comment text of a change is one tap away); peak 3 slots |
| `tapgrade-0.6.6-interrupted` | `tapgrade_0_6_6.json` | 15 | 2 findings: step 7 (the same), step 9 (a REFRESH that does not restore position) |
| `tapgrade-0.6.6-failures` | `tapgrade_0_6_6.json` | 14 | 1 finding: step 7 (the same) |

Exact steps flagged on `expensive` (asserted by `test_chain.py`; worked out by hand from the file before the code ran):

| Verifier | Steps | What is there |
|---|---|---|
| `anchoring` | 6, 7, 15, 16, 17, 24, 25 | SCAN of the tabs; DISCRIMINATE of the tabs; ENUMERATE of the folder; SCAN of the names; `.js` vs `.json`; SCAN for Apply; Apply vs Scan first |
| `memory_budget` | 7, 8, 9 | working set 5; working set 5; the RELOAD |
| `candidate_set` | 15 | the folder, paged |
| `interruption` | 2, 4, 9, 20, 28, 31 | five REFRESH that restore nothing; leaving to the chat |
| `colocation` | 26 | Apply: no preview, not everything on screen |
| `progress` | 18, 19, 27 | a TAP with no feedback; two silent WAITs |
| `causal` | 22 | the list of changes: no origin, no exclusions |
| `single_path` | 14 | the corrections picker, after Re-sync (step 7) did the same job |
| `commit_correctness` | 26 | Apply: consistency only |
| `separators` | 11, 12 | narrow to the paragraph; narrow to the sentence |

Where the transcriber interpreted OPERATION-MODEL §4 (also in the file's `notes`):

- Steps 7 and 14 carry `intent: load-corrections` with two views (`re-sync`, `corrections`): the two views that load the file.
- Step 8 (HOLD) stands for the narration's "…" where HOLD overflows.
- Step 22 (READ of the list of changes) is added to carry the cause of the wrong INFER.
- Steps 31–33 are the narration's "loop ×3". The body (refresh, re-orient, consistency check) is assumed.
- Amounts and similarities are estimates. The only numbers from the source are 66 students and 212 rows.

**Provenance of the HW1 chains.** They transcribe `docs/OPERATION-MODEL.md` §4, which is the contributing chat session's paraphrase of the owner's own narration: second hand. The narration is kept verbatim as private evidence in the course repository (speeds-kit `docs/evidence/2026-10-03-hw1-correction-narration.md`; sha256 of its text block `9823c285dcfb9e279818cf5ad19402cae8960f97b40b512eeeb09103ec8d7741`). This repository refers to it by hash only. Checks that compare a chain with what happened (#32: T1 nesting, T2 where the goal was lost, T10 predicted versus real friction) can only be judged by a reader who has that text.

The fixed flow (`fixed`) is **designed**, not observed: from the issue texts of speeds-kit #25–#31. It stays as the target the code was built toward; the flow as built is in `tapgrade_0_6_6.json` (next section). Edit steps freely. Keep these, or the tests fail on purpose:

- one REFRESH whose `restores` lists position, goal and partial (the interruption probe);
- COMMITs with a preview, everything on screen and `verify_after: correctness`;
- WAITs with visible progress and a stable view;
- a closing VERIFY of kind correctness.

## TapGrade 0.6.6: the chains the code implements

**Point.**

- `fixed` was designed before TapGrade 0.6.6 existed. `tapgrade_0_6_6.json` is what was built.
- Source: speeds-kit `docs/TAPGRADE.md` ("Applying a correction to many students — the chain") and the userscript, speeds-kit PR #33.
- A second reader checked the first draft's 37 steps against the code: 30 held, 7 were patched (three example strings, one loaded-or-not claim, and the judgment below that had silenced a verifier). Two forced WAIT steps were added.
- Provenance says `designed`: nobody has run it on real Canvas or on a phone. Amounts and similarities are guesses.

| Chain | Steps | Load | Peak slots | RELOAD | RE-ORIENT | Findings |
|---|---|---|---|---|---|---|
| `tapgrade-0.6.6` | 10 | 39.50 | 3 | 0 | 0 | 1 |
| `tapgrade-0.6.6-interrupted` | 15 | 49.75 | 3 | 0 | 1 | 2 |
| `tapgrade-0.6.6-failures` | 14 | 46.50 | 3 | 0 | 0 | 1 |

What each chain is:

- `tapgrade-0.6.6`: nothing goes wrong. Open SpeedGrader, tap Update Canvas, read where the changes come from, scan the list, (optionally) open a student, Apply, watch, read the verified line.
- `tapgrade-0.6.6-interrupted`: the page is reloaded in the middle of Apply; the person opens Update Canvas again and taps Resume.
- `tapgrade-0.6.6-failures`: 36 of 66 fail to write; the report lists each with the student, the request, the HTTP status and Canvas' own message; Retry failed. The removal of older summary comments (HW1's "Removed 18 of 54", with its own confirmation and its own retry) is a separate flow and is not modelled.

**Two findings.**

1. *Step 7 of every chain, `colocation`.* At the first Apply the collapsed rows show points before and after and a source tag; the comment text is built only when a student is opened. Not everything the decision depends on is on the screen, so each chain declares `everything_on_screen: false` and the verifier fires. This is a judgment about what "on screen" means: a before/after one tap away could be counted as on screen, and the verifier would then be silent. The file takes the stricter reading, because a silent check should be earned. Resume and Retry failed rest on a banner or a failure list and a count that are on the screen, so they are declared true. A phone cannot show 66 comments at once; what could close this is a one-line change summary on each collapsed row.
2. *Step 9 of `tapgrade-0.6.6-interrupted`, `interruption`.* After a reload the page shows the Grade view (its `view` starts as `grade` and is not stored; open or collapsed, height and pill position are). The record on the phone survives, so partial work is restored. The number on the bar comes back only after a fresh scan, so the goal rests on a bare number. The place is not restored: the person taps Update Canvas again to see `Interrupted: 42 of 66 left — Resume`. OPERATION-MODEL §5.4 asks for all three. `fixed` assumed the view would come back on Update Canvas. Storing the view would restore the view, not the open rows or the scroll place; whether `position` then counts as restored depends on what position means.

Closing both makes the interrupted chain silent. `test_chain.py` asserts that, then breaks each of ten properties of the repaired chain, one at a time: exactly the matching verifier fires.

What the numbers say, and what they do not:

- The working set peaks at 3 = B: the step's own need (1) plus 2 held (the goal, and what to expect: 212 rows, 66 students). speeds-kit's doc says "peak 2": it counts held items only. The second held item is the person's own cross-check, not something the screen forces: the screen shows both numbers, but the block that shows 212 scrolls away while the foot shows only 66. A foot reading `Apply 66 updates (212 rows)` would remove the need to hold it and lower steps 4–7 to 2.
- Load is higher than `fixed` (15.00) mostly because this chain includes the scan of 66 rows that `fixed` left out (66 coarse items × 0.25 = 16.5). Compare chains of the same task; the task here includes that scan.
- The other judgments are in the file's `provenance.note`: Apply is irreversible (no undo; the text from before stays on the phone) while Resume and Retry failed are idempotent; the tap on Update Canvas after a reload is a RE-ORIENT, as speeds-kit's doc calls it.
- Silent still means "nothing declared wrong" (`P-02be`). A chain captured from the audit's own run of the flow (`P-9d8b`) is the way to test what is declared here.

## P-2a7c integration point (design only; nothing here is built)

**Point.** P-2a7c (PR #42): decider-side working memory should run inside `explore_run`, not beside it. A chain **captured** from a driven run is that run's decision records written in this format. The budget B is the run's own working-memory limit N.

**Which chain keys carry each impairment knob** (the knobs are EXPLORE-SPEC's; the primitives are OPERATION-MODEL §6 in PR #42):

| Knob | Chain keys that carry its effect |
|---|---|
| `--working-memory N` | `budget`, `held`, `need`, the RELOAD steps |
| `--distractibility p` | `confusables` and `anchor` of the step the hijack replaced |
| `--patience k` | `feedback`, WAIT `progress_visible`, REFRESH `restores`, the RE-ORIENT steps |
| `--impulsivity` | `reading` and `amount`, COMMIT `preview_before`, `reversibility` |
| `--salience-driven` | `anchor` |

**Where B comes from.**

| Backend | The knob | State |
|---|---|---|
| browser, `checks/explore_run.py` | `--working-memory N` of EXPLORE-SPEC (it says "only the last N steps are visible"); OPERATION-MODEL §6 in PR #42 reads it as N slots: the decider keeps at most N keys | not built (P-2a7c) |
| text, `checks/explore_text.py` | `Explorer(mem_capacity=N)`: the decider's `memory` holds at most N notes | **exists**; its `note` actions are HOLD |

- The runner writes `"budget": N` on the chain it records.
- `bin/emu chain check` reads it (`--budget` overrides).
- So one N drives the decider and the verdict. No second number.

**How one decision record becomes steps** (`explore_run` log entry → chain):

| Decision record | Chain step | Filled by |
|---|---|---|
| position in the log | position in `steps` | order |
| `intention`, `rationale` | `note` (free text) | verbatim |
| `target` (`"button: Apply"`) | `target` (free text) | verbatim |
| `action.kind` click / triple / key / type | a `TAP` after the selecting step | the runner |
| `action.kind` wait | `WAIT` | the runner |
| `action.kind` scroll | `SCAN`, or `ENUMERATE` when one container scrolls two or more times | the runner |
| `hijacked: true` | the `TAP`, with "hijack" in `note` | the runner |
| (new) `op` | `op` | the policy declares which primitive it performs |
| (new) `intent_key` | `intent` | the policy |

Without a declared `op` the runner falls back on `kind` alone and says so in `note`. That records less, never something false.

**Measured by the runner, content-blind** (from the affordance view of `checks/affordances.py`: boxes, tags, salience, never text):

| Key | How |
|---|---|
| `confusables` | affordances of the same tag within ±20% of the target's box; similarity from box size and label length, never label content |
| `anchor` | `edge` if the target's box touches the viewport edge; `fixed-position` if its computed `position` is fixed or sticky; `unique-visual` if its salience is at least twice the next; else `text-keyword` if the policy matched on text; else `none` |
| `feedback` | the DOM or a screenshot hash changed within 300 ms: `immediate`; within the next wait: `delayed`; else `none` |
| `amount`, `reading` | affordances observed (coarse); the policy declares fine reads |
| `view` | a hash of the URL path and the first heading: opaque |
| `restores` | an optional probe: reload at a checkpoint, compare scroll position, the policy's `progress` count and the page's partial state |
| `held`, `need` | the decider's slot store: keys, not the page (OPERATION-MODEL §6, PR #42) |

**Declared by the policy** (it can read the page, the runner cannot judge meaning): `op`, `intent`, `source` of a RELOAD, `origin_stated` and `exclusions_stated`, `boundary_visible`.

**RELOAD.** When a needed key is not in the slot store, the runner records a `RELOAD` step with a named `source` (the task text) and the steps that follow it. Its cost is then in the load like any other.

**Illustrative only** (no code produces this yet; it loads, and `test_chain.py` asserts what it shows). With N = 2 the SCAN needs 1 slot and the run holds 2: working set 3 > B. The goal falls out; the run RELOADs it:

<!-- captured-example:json -->
```json
{"format": "emu-chain/1", "budget": 2,
 "provenance": {"source": "captured", "date": "2026-10-20", "who": "explore_run, policy tapgrade, seed 1007, N=2"},
 "steps": [
   {"op": "NAVIGATE", "held": ["goal: update Canvas"], "target": "open the page"},
   {"op": "SCAN", "amount": 9, "confusables": [3, 0.6], "held": ["goal: update Canvas", "candidate: 2nd button"], "target": "button: Update Canvas", "note": "intention: find the update button"},
   {"op": "TAP", "target": "button: Update Canvas"},
   {"op": "NAVIGATE", "held": ["candidate: 2nd button", "where I am: settings"], "target": "a settings page opened", "note": "the goal fell out of the 2-slot store"},
   {"op": "RELOAD", "source": "task text", "held": ["goal: update Canvas", "where I am: settings"], "target": "re-read the task"}]}
```

**Done when** (extends P-2a7c): a scripted run writes a captured chain; `bin/emu chain check` reads it; the chain's `budget` equals the run's N; the number of RELOAD steps equals the runner's own count of dropped keys that were needed later; a sweep over N shows the budget findings appear as N falls.

**Cheapest first step:** the text backend. It needs no browser and already bounds the decider's memory.

## Decisions taken (where the model or the brief was silent)

| Decision | Why | Change it in |
|---|---|---|
| The working set is `need` + `held`; B flags the sum | §3 lists "slots needed now" and "held across the step"; DISCRIMINATE needs 2+ at once | `chain_load.py`, `memory_budget` |
| `TAP` is a 16th op, zero cost | §4 writes it in both chains | `OPS` in `chain.py` |
| Defaults per op for `need` and `reading` | a plain step is one short line | `OP_DEFAULTS` |
| Look-alikes start at similarity 0.5 | §5.1 gives no number | `--lookalike` |
| `times` for "loop ×3" | the narration says ×3; unrolling hides it | a step key |
| RELOAD written flat; `source` required | §1: a RELOAD is a chain; P-2a7c wants a named source | `chain.py` |
| A loop is a REFRESH right after a WAIT or a VERIFY, or right after a REFRESH that was one | mechanical and testable; `times: n` equals n copies in every count (a test asserts it) | `chain_load.py` |
| `commit_correctness` also wants a later VERIFY of the right kind | the chain should show the person seeing the check; it is the one reader of VERIFY `kind` | `chain_verifiers.py` |
| `progress` also flags `feedback: none` on any step | an unacknowledged action starts the WAIT/REFRESH loop (§1) | `chain_verifiers.py` |
| `reversibility` sets how strict two verifiers are: an `idempotent` COMMIT needs no preview and may stop at consistency | §1: irreversibility multiplies the cost of an error; the label is the narrator's claim | `colocation`, `commit_correctness` |
| One finding per step per verifier, reasons joined | "the steps it flags" stays a clean list | `chain_verifiers.py` |
| Exit 2 for an invalid file; one file may hold several chains | 1 means "has findings"; the HW1 pair is one narration | `chain_check.py` |

## What stays open

| Id | What | Closes when |
|---|---|---|
| `P-9d8b` | chains cannot yet be captured from a driven session (the "later" half of #32) | the design above is built and tested on the text backend, then on `explore_run` |
| `P-02be` | verifiers read declared properties, so a chain can pass by omission | the declared properties are measured on a captured chain and compared with a narrated chain of the same task |
| `P-67a1` | the load weights are ordinal and uncalibrated | the weights are fitted or checked against timed narrations or measured runs |
| `P-2a7c` | running the budget inside `explore_run` (PR #42) | see its entry, and "Done when" above |

### Approximations confirmed by an independent review of PR #43

None changes a documented number. Each is a case of P-02be (a verifier reads what the narrator declared) or a default that is easy to misread.

- A `HOLD` counts its own item twice: `need` 1 plus the item in `held`. `HOLD[a]`, `HOLD[a,b]`, `HOLD[a,b,c]` flags the third step (demand 4 against B = 3); the same list with `need: 0` is silent. Write `need: 0` on a HOLD whose only demand is the item it holds. The HW1 peak of 5 counts it.
- `candidate_set` is silent when `set_visibly_complete` is true, however many `pages` were turned.
- `commit_correctness` accepts any later VERIFY of the right kind, including one under another `intent`; `COMMIT, COMMIT, VERIFY` passes.
- A NAVIGATE with no `restores` is silent in `interruption`; an irreversible `TAP` with no COMMIT is invisible to `colocation`; a SCAN with no `confusables` is silent in `anchoring`.
- `amount` times `times` can overflow to `Infinity` in `--json`, with absurd values only.

This layer does **not**: measure any person; read a page; capture a session; set a threshold on the load; judge whether a narration is true.

