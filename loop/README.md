# loop: a closed loop around an assistant session

`bin/emu` is the engine: it evaluates what a reader meets. `bin/loop` is the harness that calls it, and calls everything else a session would otherwise have to remember. Standard library only. No data of any project: a project names its own files in one `loop.json`.

Extracted on 2026-11-10 from a private project in which each part had been running under tests. Here the parts are one package with one entry and one configuration; what belongs to that project stayed there (last section but one).

## Why a loop
An assistant forgets, and the person it works for (the principal) cannot re-read everything. A rule that depends on being remembered is a wish: `docs/OPEN-PROBLEMS.md` records a requirement that lived in prose and stayed unbuilt across sessions (P-8c1e), and feedback that must be asked for and so never reaches a session that does not ask (P-dae1). So each step below is run by a hook or by the tick, never by memory, and each says what it did not check.

```
the principal speaks
  -> record   bank it: once, verbatim, with its time (also what was typed while a turn was running)
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
| `record` | `bank`, `raw`, `find` | every utterance of the principal is banked once, verbatim, with its time | a typed message is in the transcript and not in the bank |
| `gate` | `check`, `render`, `baseline`, `selftest` | a wait carries a chain of verbatim quotes down to a root, or a closure in the principal's words | a status changes and the debt list does not; a question is cited as an assertion |
| `tick` | `run`, `liveness` | the due check runs and nothing starves | a check has not run for three times its interval and no tick said so |
| `hook` | `install`, `prompt`, `post`, `stop`, `compact` | the loop is closed by the session's own events, not by memory | a stop is refused more than `stop_cap` times in a row; a hook breaks a tool call |
| `guard` | `pre`, `permissions` | no merge, no write to a protected branch and no rewritten history without a recorded verdict | such an act passes with no verdict that names it |
| `keep` | `backup`, `restore`, `replay` | what a later session needs survives the machine | a file exists nowhere but in a machine that is gone |
| `doctor` | prints what the loop can see from here | changes nothing | it writes anything |

Every module's docstring carries two lines, `INVARIANT:` and `FAILS WHEN:`. `loop/tests/test_selfcheck.py` asserts that, and asserts this table against the code.

## Start
```
python3 -I bin/loop doctor                  # what is found from this directory
python3 -I bin/loop hook install --user     # the user-level settings: the channel seen to fire in cloud sessions
```
The installed commands carry the project's root, so they work from any working directory.

## Configuration (`loop.json` at the project root; every key optional; an unknown key is refused)
| Key | Default | What it is |
|---|---|---|
| `principal_method` | `PRINCIPAL-METHOD.md` | the principal's own text, printed at every prompt and every `reread_every` tool calls |
| `reread_every` | 5 | how many tool calls between two reprints |
| `bank` | `loop-state/bank.jsonl` | append-only, in git: one record per utterance |
| `words` | none | globs of more files that hold the principal's words, for `record find` |
| `not_principal_prefixes` | none | a text that starts with one of these is not the principal's |
| `tree`, `chain_debt`, `clause_bank_dir` | under `loop-state/` | the goals and questions, the waits that had no chain at the first run, the bank cut into clauses |
| `verdicts` | `loop-state/verdicts.jsonl` | an advisor's verdicts, recorded before a guarded act |
| `protected_branches` | `main` | where a write needs a verdict |
| `backup` | remote `origin`, prefix `backup/` | where a stop keeps the transcript, the scratch files and what is untracked |
| `transcripts_dir` | `~/.claude/projects` | where the session transcripts are |
| `state_dir` | `.loop` | counters and logs; never committed |
| `checks` | none | what `tick` runs: a name, a verb with its arguments, an interval |
| `stop_runs` | keep, then record | what every stop runs; a failure is reported and never blocks |
| `stop_blocks_on` | none | commands whose failure refuses the stop |
| `stop_cap` | 3 | how many refusals in a row before the stop is let through |

## Rules the package keeps for itself
- **Fail closed.** A missing tree, bank or transcript is a finding, not a pass.
- **Say what was not checked.** A result names what ran and what did not, so silence is not read as closure.
- **A refusal is capped.** A stop that can be refused without limit is a trap; the count is kept and the cap is a setting.
- **Append, never rewrite.** The stores are append-only; an overwrite leaves a dated copy.
- **The builder is not the verifier.** A module is ported by one worker and accepted by another reader who runs its tests again.
- **A budget.** This file has at most 120 lines, and a test holds it to that.

## What stays in the instance
The principal's method text, the contents of the bank, the tree, the verdicts, the permission rules, the prompts of its recurring jobs, and every tool of the project's own subject. None of that is here, and a test refuses it.

## What it does not do
- It does not judge meaning. A gate checks that a source exists and resolves, not that the reading of it is right.
- It does not evaluate pages. That is the engine; name its command in `stop_blocks_on`.
- It has run in one kind of container. Whether a hook registered in the middle of a session fires is not established here.
