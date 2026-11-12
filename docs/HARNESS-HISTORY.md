# Harness and engine: evidence and lineage

This is a bounded extraction record, read on 2026-11-11, not a claim to have exhausted the history or established scientific validity. Repository statements and reported experiments below retain their original scope. No cited research paper was independently reread in this extraction.

## Baseline and verification

Start at [PR #85](https://github.com/yulinl2/drunken-emu/pull/85), its discussion and commits, not the default branch. The extracted upstream baseline is [`9a483c07859d205474ba573fc5deb7cdf18df3d5`](https://github.com/yulinl2/drunken-emu/commit/9a483c07859d205474ba573fc5deb7cdf18df3d5), branch `claude/harness-engine-design-extract-o54mh1`; the PR was open when read.

GitHub reported success for that exact head's [push run](https://github.com/yulinl2/drunken-emu/actions/runs/42937078095) and [PR run](https://github.com/yulinl2/drunken-emu/actions/runs/42937081694). These are remotely observed CI outcomes, not a new local execution or evidence of semantic effectiveness. The PR body's six-verb inventory and test counts predate later commits; use the pinned code and this extraction's own test report for their respective states.

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

`bin/emu verdict` evaluates; `bin/loop watch` orchestrates a configurable command. The command protocol is exit 0 for pass, 3 for not evaluated, other exits for fail, with optional final JSON containing `vector` and `layers`. Candidate identity includes artifact bytes, declared input bytes and command. The evaluator program's bytes are covered only when declared as inputs. A source-resolution gate checks provenance links, not the correctness of interpretation; the guard is a documented tripwire, not a security boundary.

The instance supplies its principal's method, bank, goal tree, verdict content, permission policy, recurring prompts and subject-specific tools. Claude hooks, transcript parsing and mods are host adapters. Bash/GNU/flock backup is a platform adapter. Neither adapter is evidence of universal portability.

The pinned [manual](https://github.com/yulinl2/drunken-emu/blob/9a483c07859d205474ba573fc5deb7cdf18df3d5/loop/README.md) and [sandbox record](https://github.com/yulinl2/drunken-emu/blob/9a483c07859d205474ba573fc5deb7cdf18df3d5/docs/SANDBOX-FACTS.md) report one Nov10 live session: capped Stop refusal, forced-push refusal, backups and bank/liveness worked. They also report no PostToolUse feedback observed in 34 calls and no reprint at a notification prompt. This supersedes the older PR body's "not installed live" statement without claiming general live success.

Open scientific questions remain [checker gaming #69](https://github.com/yulinl2/drunken-emu/issues/69), [held-out improvement #70](https://github.com/yulinl2/drunken-emu/issues/70), [coverage disclosure #71](https://github.com/yulinl2/drunken-emu/issues/71), [meaning of oracle-ish #74](https://github.com/yulinl2/drunken-emu/issues/74) and [which Oolong-Pro pattern #75](https://github.com/yulinl2/drunken-emu/issues/75). Fixture separation, CI success and automatic invocation do not settle them. Preserve competing readings and earlier evidence; supersede claims when new observations warrant it.
