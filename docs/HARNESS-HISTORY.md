# Harness and engine: evidence and lineage

This is a bounded extraction record, first read on 2026-11-11 and refreshed on 2026-11-12, not a claim to have exhausted the history or established scientific validity. Repository statements and reported experiments below retain their original scope. No cited research paper was independently reread in this extraction.

## Baseline and verification

Start at [PR #85](https://github.com/yulinl2/drunken-emu/pull/85), its discussion and commits, not the default branch. The current upstream baseline is [`d444a0031a92104473e7949241d75a67167e84f2`](https://github.com/yulinl2/drunken-emu/commit/d444a0031a92104473e7949241d75a67167e84f2), branch `claude/harness-engine-design-extract-o54mh1`; on 2026-11-12 the PR remained open with 35 commits. The previous extraction baseline, [`9a483c07859d205474ba573fc5deb7cdf18df3d5`](https://github.com/yulinl2/drunken-emu/commit/9a483c07859d205474ba573fc5deb7cdf18df3d5), remains a historical checkpoint.

GitHub was queried again on 2026-11-12: the exact `d444a00` head's [push run](https://github.com/yulinl2/drunken-emu/actions/runs/43027275515) and [PR run](https://github.com/yulinl2/drunken-emu/actions/runs/43027285965) both completed successfully on Nov11. The previous head also had successful [push](https://github.com/yulinl2/drunken-emu/actions/runs/42937078095) and [PR](https://github.com/yulinl2/drunken-emu/actions/runs/42937081694) runs. These are remotely observed CI outcomes, not a new local execution or evidence of semantic effectiveness. The PR body's six-verb inventory and test counts predate later commits; use the pinned code and this extraction's own test report for their respective states.

| Commit | Evidence retained in the design |
|---|---|
| [`1b38ea4`](https://github.com/yulinl2/drunken-emu/commit/1b38ea45163316b119b78b6192f478ae2f85ad9c) | Six existing components joined under one configuration; joined tests exposed gaps between record/gate, project/kit paths, session identity and backup failures. |
| [`81e0351`](https://github.com/yulinl2/drunken-emu/commit/81e03513789737b4d2ee30fb7776653223739655) | Engine verdict became a standalone command; serialized smoke evaluation prevents concurrent runs judging each other's pages. |
| [`121236c`](https://github.com/yulinl2/drunken-emu/commit/121236c5587bd459ec16d5f6030ddbdfc4bea275) | Generic watch invokes arbitrary checks, retains candidate bytes and verdicts, and caps Stop refusals. |
| [`6a2cb5c`](https://github.com/yulinl2/drunken-emu/commit/6a2cb5c5640370dc1440622bcad1ab11f8da8216) | Declared inputs, torn-ledger handling, event budgets, lock outcomes and coverage disclosure close false-pass routes. |
| [`632bfc7`](https://github.com/yulinl2/drunken-emu/commit/632bfc7a147601e465f2353d8bb53191107f788a) | Old evaluator-specific loop superseded by a compatibility stub; all 29 prior tests mapped, with deliberate omissions explained. |
| [`81d2395`](https://github.com/yulinl2/drunken-emu/commit/81d2395bc4b437834bbdcadd8312c5d73d0a687e) | Inputs rehashed after evaluation: changed inputs cannot inherit a PASS for their previous bytes. |
| [`a02ee80`](https://github.com/yulinl2/drunken-emu/commit/a02ee80d3152cd795680b6a5e2414f7fc2d7d924) | Revisit registry retains questions and append-only events. |
| [`ebd3c6d`](https://github.com/yulinl2/drunken-emu/commit/ebd3c6dfd6f218a6973025f9b202649d52a146a1) | Verdict writer validates an on-disk review answer and merge head before recording it. |
| [`9a483c0`](https://github.com/yulinl2/drunken-emu/commit/9a483c07859d205474ba573fc5deb7cdf18df3d5) | Record search, quote checking and gate share one reader of principal-word lines. |
| [`46f47ab`](https://github.com/yulinl2/drunken-emu/commit/46f47ab2d4e3521ffb166f493456c0434ec925b9) | Backup diagnostics distinguish local, pushed, unreachable and absent status; after local state loss, a bounded shallow fetch reads the session's pushed status in a scratch repository. A waited backup checks its own local result only. |
| [`38b59ae`](https://github.com/yulinl2/drunken-emu/commit/38b59aec156c7219562f8bcf645c7336e8457762) | Hook wrappers separate guard refusal, usage error and runtime failure; a failed guard invokes the shared fallback rule, with explicit gaps retained as P-dcf8. |
| [`d444a00`](https://github.com/yulinl2/drunken-emu/commit/d444a0031a92104473e7949241d75a67167e84f2) | Gate and revisit share one tree loader: return the whole valid tree or refuse it with faults; duplicate IDs and malformed nodes cannot silently disappear. Manuals clarify that engine evaluation requires explicit project configuration. |

The [retirement map](https://github.com/yulinl2/drunken-emu/blob/9a483c07859d205474ba573fc5deb7cdf18df3d5/docs/EMU-LOOP-RETIRED.md) is the detailed behavioral reconciliation; retain it rather than recreating a competing loop or silently dropping old guarantees.

## Why these components exist

- [#32](https://github.com/yulinl2/drunken-emu/issues/32): a replayable motor-action list cannot alone explain task cost, goal loss, intention or wrong inference. Its record-format alternatives remain candidates judged against ten test points.
- [#59](https://github.com/yulinl2/drunken-emu/issues/59): forgetting can remove stale framing and make durable records necessary. Rereading is a cheaper candidate than new machinery. Reported gate-satisfying behavior did not necessarily satisfy the gate's purpose.
- [#66](https://github.com/yulinl2/drunken-emu/issues/66), [#67](https://github.com/yulinl2/drunken-emu/issues/67), [#68](https://github.com/yulinl2/drunken-emu/issues/68): evaluation requested only by the agent may never run; whether hooks improve this requires observed delivery, a baseline and coverage disclosure.
- [#84](https://github.com/yulinl2/drunken-emu/issues/84): emerging tools should be revised while used, but the wrapper also needs a test that fails on a planted fault. An in-session timer was observed not to survive container restart.

The motivating circuit-discovery paper in #66 was identified from owner-supplied screenshots with an incomplete arXiv identifier. That historical motivation is not independently verified literature evidence here. #32 cites KLM/GOMS, hierarchical task analysis, cognitive walkthrough, information foraging, working-memory models, ACT-R and distributed tracing as prior art, not novel ingredients of this package.

## Records, lenses and leakage

[`theory/RECORD-THEORY.md`](https://github.com/yulinl2/drunken-emu/blob/9a483c07859d205474ba573fc5deb7cdf18df3d5/theory/RECORD-THEORY.md) is a hypothesis-bearing theory track, not the implemented interchange format or a validated cognitive model. It distinguishes immutable sources (L0), attributed assertions (L1) and reproducible views under explicit lenses (L2). An assertion's speaker, encoder, modality, scope and evidence are distinct: faithful quotation does not establish truth.

A lens names admitted sources, conflict treatment and defaults. Unknown, asserted absent and default are different states. FINDING/PASS/UNDECIDED describes a verifier's knowledge; these theory labels do not silently redefine the runtime command protocol.

Predictors belong on the input side; behavior, outcomes, beliefs and opinions retain their roles. Checking a narration against its own outcome labels risks restating the complaint. The historical pressure model's items were encoded after outcomes were read and its capacity was selected on the same task: its numerical tables are structural diagnostics, explicitly not validation. Attribution rules and permitted event orders can change conclusions and must be recorded.

The proposed independent test fixes artifact-derived predictors, capacity and predictions before a new real task, then scores held-out observations. Semantic label/intent equivalence remains an attributed judgment. No passing parser, source-resolution gate or unit suite replaces that reading.

## Reusable boundary and remaining questions

`bin/emu verdict` evaluates; `bin/loop watch` orchestrates a configurable command. Engine evaluation runs only when the project configures it; defaults do not. The evaluator command protocol is exit 0 for pass, 3 for not evaluated, other exits for fail, with optional final JSON containing `vector` and `layers`; hook-wrapper exit codes are a separate host protocol. Candidate identity includes artifact bytes, declared input bytes and command. The evaluator program's bytes are covered only when declared as inputs. A source-resolution gate checks provenance links, not the correctness of interpretation; the guard is a documented tripwire, not a security boundary.

The instance supplies its principal's method, bank, goal tree, verdict content, permission policy, recurring prompts and subject-specific tools. Claude hooks, transcript parsing and mods are host adapters. Bash/GNU/flock backup is a platform adapter. Neither adapter is evidence of universal portability.

The current pinned [manual](https://github.com/yulinl2/drunken-emu/blob/d444a0031a92104473e7949241d75a67167e84f2/loop/README.md) and [sandbox record](https://github.com/yulinl2/drunken-emu/blob/d444a0031a92104473e7949241d75a67167e84f2/docs/SANDBOX-FACTS.md) still report one Nov10 live session: capped Stop refusal, forced-push refusal, backups and bank/liveness worked. They also report no PostToolUse feedback observed in 34 calls and no reprint at a notification prompt. The Nov12 refresh found no newer live observation there; these reports predate the three new commits and do not validate their deployment. This supersedes the older PR body's "not installed live" statement without claiming general live success.

The new failure behavior leaves [P-dcf8](https://github.com/yulinl2/drunken-emu/blob/d444a0031a92104473e7949241d75a67167e84f2/docs/OPEN-PROBLEMS.md) open: fallback coverage is partial, no Python means no check, host timeout can let a call through, and the fallback can over-block repair commands. Tests and CI cover specified cases; no fresh live-host run is claimed here. A pushed backup's first line can still say `running since` because it was captured before push completion; its source and previous-run line must remain visible rather than being presented as current convergence.

Open scientific questions remain [checker gaming #69](https://github.com/yulinl2/drunken-emu/issues/69), [held-out improvement #70](https://github.com/yulinl2/drunken-emu/issues/70), [coverage disclosure #71](https://github.com/yulinl2/drunken-emu/issues/71), [meaning of oracle-ish #74](https://github.com/yulinl2/drunken-emu/issues/74) and [which Oolong-Pro pattern #75](https://github.com/yulinl2/drunken-emu/issues/75). Fixture separation, CI success and automatic invocation do not settle them. Preserve competing readings and earlier evidence; supersede claims when new observations warrant it.
