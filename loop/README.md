# loop: a closed loop around an assistant session

`bin/emu` is the engine: it evaluates what a reader meets. `bin/loop` is the harness that calls it, and calls everything else a session would otherwise have to remember. Standard library only. No data of any project: a project names its own files in one `loop.json`.

Extracted on 2026-11-10 from a private project in which each part had been running under tests. Here the parts are one package with one entry and one configuration; what belongs to that project stayed there (last section but one).

## Why a loop
An assistant forgets, and the person it works for (the principal) cannot re-read everything. A rule that depends on being remembered is a wish: `docs/OPEN-PROBLEMS.md` records a requirement that lived in prose and stayed unbuilt across sessions (P-8c1e), and feedback that must be asked for and so never reaches a session that does not ask (P-dae1). So each step below can be run by a hook or by the tick instead of by memory, and each says what it did not check. Out of the box the hooks run `record`, `keep`, the reprint and the guard; `gate` and `tick` run once the project's `loop.json` names them (see Start).

```
the principal speaks
  -> record   bank it: once, verbatim, with its time (also what was typed while a turn was running: shown at the next tool call)
  -> gate     nothing unsourced: a wait must cite a record; a missing input reads as changed
  -> tick     one due check per tick; a missed check moves to the front; a starved check is raised
  -> hook     every prompt: the principal's method again; every Nth tool call: again;
              every stop: keep, record, then the gates and the engine (a refusal is capped)
  -> guard    a merge or a write to a protected branch only on a verdict recorded before the act
  -> keep     backup at every stop and before every compaction; restore; rebuild lost files from the transcript
  -> the principal reads less; what they say next is a new record
```

## Verbs (`python3 -I bin/loop VERB ...`)
| Verb | Does | Guarantees | Shows it failed when |
|---|---|---|---|
| `record` | `bank`, `raw`, `find`, `pending` | every utterance of the principal is banked once, verbatim, with its time | a typed message is in the transcript and not in the bank |
| `gate` | `check`, `render`, `baseline`, `selftest` | a wait carries a chain of verbatim quotes down to a root, or a closure in the principal's words | a status changes and the debt list does not; a question is cited as an assertion |
| `tick` | `run`, `liveness` | the due check runs, one tick at a time, and `run` exits 1 when its check failed; nothing starves | a check has not run for three times its interval and no tick said so |
| `hook` | `install`, `prompt`, `post`, `stop`, `compact` | what the project's `loop.json` names is run by the session's own events, not by memory; every tool call shows the principal's queued words, each once; the steps and checks of an event share one time budget (`HOOK_TIME` in `loop/hook.py`), which ends before the timeout install writes | a stop is refused more than `stop_cap` times in a row; a hook breaks a tool call; a queued message still waiting is shown at no tool call; a hook runs past the timeout install wrote |
| `guard` | `pre`, `permissions` | a tripwire, not a barrier: a merge, a write to a protected branch or a forced push needs a verdict recorded before the act; the known gaps are listed in `loop/guard.py`; under `sessions: here` it reads sessions inside the project | such an act, in a form the guard reads, passes with no verdict that names it |
| `keep` | `backup`, `restore`, `replay` | what a later session needs survives the machine | a file exists nowhere but in a machine that is gone |
| `watch` | `eval`, `status` | a changed watched file, or a changed input it names, gets a verdict from its check; the verdict reaches the session after the edit; a PASS says what its check did not run; a stop waits while the newest verdict fails, is not evaluated (out of time, lock held) or is dominated | a watched file's or an input's bytes changed and the next stop passes with no record for them; a PASS hides what did not run; a ledger line that is not a record is read as one |
| `doctor` | prints what the loop can see from here | changes nothing | it writes anything |

Every module's docstring carries two lines, `INVARIANT:` and `FAILS WHEN:`. `loop/tests/test_selfcheck.py` asserts that, and asserts this table against the code. `loop/tests/test_closed_loop.py` runs one session through all six in a temporary project, with the output of each verb as the input of the next; on 2026-11-10 it found five defects that the verbs' own tests could not, and two reviews of the package found more that it now pins: a stop acts on the session that stopped, not on the newest transcript of the machine; each session has its own backup; a trial takes nothing.

## The mod (`loop/mod/`): what a hook cannot do
A hook is a command: it cannot read the session's usage or start a compaction. A mod (a plugin with a hooks module, which the engine loads) can. This one registers two tools the model calls and one hook, and decides nothing itself.
| Part | Does | Seen (`docs/SANDBOX-FACTS.md`, 2026-11-10) |
|---|---|---|
| `usage` | the context's fill, each rate-limit window's percent used and reset time, the session's cost | live figures inside a turn, where the host's own record of the session lagged a whole turn |
| `compact` | starts a compaction once the turn has ended, with the principal's line and one pointer to the session's state file | started by a session itself, in two sessions; each summary carried the text |
| every compaction | adds the same two texts, also to a typed or an automatic one; logs tokens and cost before and after | in both sessions |

It loads at a session's start from a skills folder: `.claude/skills/loop` here is a link to it, and a fresh session had both tools with no person involved. A copy placed in `~/.claude/skills/` in the middle of a session was not loaded. Its state is in `~/.claude/loop/`: `line.txt` (the principal's line: the project's own words, none here), `also-keep.txt` (one line: where the session's state file is; the line selects, the file carries the state) and `log.jsonl`.

## Start
```
python3 -I bin/loop doctor                  # what is found from this directory
python3 -I bin/loop hook install --user     # the user-level settings: the channel seen to fire in cloud sessions
```
The installed commands carry the project's root, so they work from any working directory. `install` first tries each command once on an empty payload: the command must start and read its configuration. A trial banks nothing and backs nothing up. `install` refuses where there is no `loop.json`: a project names itself.

That installs `record`, `keep`, the reprint and the guard. To close the rest of the loop, the project's `loop.json` names where a stop is refused and what the tick runs; the tree the gate reads is a source, written by hand:
```
{"backup": {"remote": "<a private remote>"},
 "stop_blocks_on": [["gate", "check"]],
 "stop_runs": [["keep", "backup"], ["record", "bank"], ["tick", "run"]],
 "checks": [{"name": "gate", "run": ["gate", "check"], "every_s": 3600}]}
```

## Configuration (`loop.json` at the project root; every key optional; an unknown key is refused)
| Key | Default | What it is |
|---|---|---|
| `principal_method` | `PRINCIPAL-METHOD.md` | the principal's own text, printed at every prompt and every `reread_every` tool calls |
| `reread_every` | 5 | how many tool calls between two reprints |
| `bank` | `loop-state/bank.jsonl` | append-only, in git: one record per utterance |
| `words` | none | globs of more files that hold the principal's words, for `record find` |
| `not_principal_prefixes` | none | a text that starts with one of these is not the principal's |
| `tree`, `chain_debt`, `clause_bank_dir` | under `loop-state/` | the goals and questions, the waits that had no chain at the first run, the bank cut into clauses (optional: without that folder the gate reads `bank`) |
| `verdicts` | `loop-state/verdicts.jsonl` | an advisor's verdicts, recorded before a guarded act |
| `protected_branches` | `main`, `master` | where a write needs a verdict |
| `backup` | no remote, prefix `backup/` | where a stop keeps the stopping session's transcript (with those of the agents it started), the extra folders and what is untracked. Name a **private** remote: a transcript holds everything the session saw |
| `transcripts_dir` | `~/.claude/projects` | where the session transcripts are |
| `sessions` | `here` | which sessions the hooks act for. `here`: a session whose working directory at the event is the root or under it. Its whole transcript is then taken, with what it typed elsewhere; a session that starts above the root (a cloud session with several repositories) is not served until it enters, and nothing says so. `all`: at every stop of any session on this machine, that session's words go into this project's bank and every transcript under `transcripts_dir` to this project's remote, and a verb run by hand takes the newest transcript; for a machine whose every session is this project's |
| `state_dir` | `.loop` | counters and logs; never committed |
| `checks` | none | what `tick` runs: a name, a verb with its arguments, an interval |
| `stop_runs` | keep, then record | what every stop runs; a failure is reported and never blocks |
| `stop_blocks_on` | none | commands whose failure refuses the stop |
| `stop_cap` | 3 | how many refusals in a row before the stop is let through |
| `watch` | none | entries `{"name", "files": [glob, ...], "run": [word, ...]}`, and optionally `"inputs": [glob, ...]`: `{path}` in `run` is the judged file; a verdict is for its bytes and those of its inputs (the state folder never counts as one); records in `.loop/watch.jsonl`; an unknown key is refused |

**`loop.json` is code.** Its commands (`stop_runs`, `stop_blocks_on`, `checks`) run with your rights at every stop; the file it names is printed into every prompt; its backup remote receives the transcripts; the bank is committed. A `loop.json` that arrives by clone, pull, checkout or merge takes effect at the next hook, so review it as code. With `--user` the hooks sit in the settings of every session on this machine; they act only for sessions inside the project unless `sessions` is `all`. Install the loop for a private project.

## Rules the package keeps for itself
- **Fail closed.** A missing tree, bank or transcript is a finding, not a pass.
- **Say what was not checked.** A result names what ran and what did not, so silence is not read as closure.
- **A refusal is capped.** A stop that can be refused without limit is a trap; the count is kept and the cap is a setting.
- **Three kinds of file.** A log is only appended (the bank, the verdicts, the tick log). A source holds judgement kept by hand and is replaced only with a dated copy (the tree, the debt list). A view is recomputed and never edited (the gate's report, liveness). Regenerating a source loses what no script can make again.
- **A failure reaches the session unasked.** A backup that did not succeed is said at the next prompt and shown by `doctor`.
- **The builder is not the verifier.** A module is ported by one worker and accepted by another reader who runs its tests again.
- **A budget.** This file has at most 120 lines, and a test holds it to that.

## What stays in the instance
The principal's method text, the contents of the bank, the tree, the verdicts, the permission rules, the prompts of its recurring jobs, and every tool of the project's own subject. None of that is here, and a test refuses it.

## What it does not do
- It does not judge meaning. A gate checks that a source exists and resolves, not that the reading of it is right.
- It does not evaluate pages. That is the engine; name its command in `stop_blocks_on`.
- It does not let due checks take turns yet: a check that keeps failing is picked first at every tick, the others wait until they are more than three intervals late, and `tick liveness` then names them.
- `record find` reads the words files only inside quotation marks; the principal's words outside quotes are not found there.
- No verb writes a verdict: the line is written by hand, and the guard refuses a malformed one.
- The reprint also reaches the workers a session starts. Four of the six that ported this package took it for foreign text and ignored it; whether a worker should be bound by it is open.
- It cannot tell a public remote from a private one, which is why `backup.remote` has no default: until a project names one, `keep backup` refuses and every prompt says that nothing is kept.
- `keep backup` needs bash 4, GNU coreutils and findutils, and `flock`; it has not run on macOS. Each session keeps its own backup worktree under the state folder, and old ones are not removed yet.
- A user-level install replaces a symlinked settings file with a regular one. `guard permissions apply` removes a rules file's retired asks even where no guard is registered.
- The hooks name the kit's clone by its path. If that clone is moved or deleted, the hooks do nothing, the guard included, and every prompt says that the kit is gone: run `hook install` again from where the kit is now.
- `watch` judges only what `loop.json` names, when a hook or `watch eval` runs. A watched file deleted on purpose is judged gone at every stop: the stop is refused up to `stop_cap` times, then let through, and no verb clears that record (the ledger is only appended to). A tool call does not wait for `watch.lock`: when another run holds it, the call says so and judges nothing; a stop waits for it inside its budget and refuses what it could not judge. A ledger line that is not a record is skipped and said once per run, and its bytes are judged again.
- It has run in one kind of container. Its hooks ran live in one session on 2026-11-10: a stop was refused three times and let through at the cap, the guard refused a forced push, each stop made a backup, the bank and `tick liveness` answered. Not seen there: any text from the PostToolUse hook in 34 tool calls, and a reprint at a prompt that was a notification; why is not established. User-level hooks written by a session's own first command were seen to fire for the rest of that session (`docs/SANDBOX-FACTS.md`, 2026-11-10); a project-level `settings.local.json` written mid-session left no trace (same file, 2026-10-17).
- `record pending` counts a queued message as delivered when a later row contains its text, so a short queued word that a later message contains (`y` in `yes`) is not listed.
