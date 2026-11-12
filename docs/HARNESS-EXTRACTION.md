# Reusable harness and evaluator boundary

This extraction starts at [PR #85](https://github.com/yulinl2/drunken-emu/pull/85),
head `d444a0031a92104473e7949241d75a67167e84f2` on 2026-11-12, with
`9a483c07859d205474ba573fc5deb7cdf18df3d5` kept as the earlier checkpoint,
not at the default branch.
Reason: that head already consolidates the latest tested session loop and retires
the older engine-specific harness. Export its implementation; do not fork a
second implementation. [History](HARNESS-HISTORY.md) preserves the reasons,
source links, superseded designs and unsettled scientific questions.

## Ends and acceptance

Make session mechanisms reusable without carrying any project's utterances,
decisions, credentials or evaluator dependencies. An independent directory must
run a real checker, retain its evidence, notice changed inputs and report failure.
The resulting package is a source distribution for Python on POSIX, not a claim
that every assistant host or operating system supports its adapters.

## Boundaries

| Part | Responsibility | Outside its guarantee |
|---|---|---|
| `loop/config.py`, `watch.py`, `tick.py` | Configuration, due work, evaluator invocation, candidate identity, recorded outcomes | Whether a chosen check answers the actual goal |
| `record.py`, `gate.py`, `revisit.py` | Source retention, resolvable quotation chains, append-preserving revisits | Correct attribution, interpretation, or a justified closure |
| `guard.py` | Recognised command tripwire; record a supplied advisor answer before an act | A security boundary or independently generated advisor judgment |
| `hook.py`, transcript readers, `mod/` | Claude event/transcript/compaction adapters | Codex integration or portable event delivery |
| `keep.py`, `keep_backup.sh` | Session-specific backup/restore/replay | Universal platform support or losslessness when input was never captured |
| `adapters/emu.py` | Existing emu-specific coverage interpretation | Generic orchestration policy |
| External evaluator | Define and execute subject-specific checks | Authority to redefine the principal's goal |
| Instance `loop.json` and its files | Own goals, sources, policies, check commands and private backup destination | Reusable runtime data |

The `bin/emu` engine remains in this repository with its browser/chain dependencies;
it is one evaluator of the harness, not a required dependency of its export.
The minimal scaffold supplies a different, dependency-free evaluator so this
boundary is exercised. Browser functionality is not silently copied or advertised
as part of the smaller package.

## Evaluator interface (existing behavior)

`watch` runs an argv list from the instance root, replacing `{path}` with the
watched file. Exit **0** means pass, **3** means not evaluated, any other exit means
failure. A command that cannot start or exceeds its budget is not evaluated.
The optional final nonempty stdout line is JSON with `vector` (numeric axes,
lower is better) and `layers` (names to status strings). Exit status wins over a
contradictory JSON `gate`; other output is diagnostic text.

A candidate includes artifact bytes and the path/hash pairs of declared `inputs`;
the command has its own identity. Declare the evaluator script and its policy as
inputs: the command string alone does not identify their bytes. Inputs and artifact
are checked again after execution; changed bytes invalidate that run. This is not
an atomic filesystem snapshot: an adversarial change-and-restore during a check,
undeclared dependencies, interpreter versions and remote services remain outside
that identity. Use a hermetic evaluator when the task needs that stronger claim.

PASS is bounded by coverage. Dominance compares shared numeric axes within a check,
path and command; keep axis meanings and coverage comparable. Missing dimensions
are not evidence of improvement. A semantic reader or held-out outcome remains
necessary where no mechanical checker can decide the goal.

## Preservation and supersession

The runtime is reused, not rewritten. Export records hashes, modes and provenance;
it contains no `.git`, runtime state, transcripts or instance source files. History
stays in Git; use `git bundle` if history itself must move. The original checkout
and PR head remain intact. The old harness compatibility stub and its explicit
[29-test migration map](EMU-LOOP-RETIRED.md) remain in the source repository.

Evidence logs append; generated views can be rebuilt; human-authored source needs
retained predecessors. These distinctions also govern this document: source links
keep compressed claims inspectable, and new evidence can supersede this summary.
No checksum or successful export establishes semantic equivalence by itself.

## Use and validation

See the exported root README for the minimal scaffold and verification commands;
see `loop/README.md` for all verbs and host adapters. Hooks are not installed by
export. The scaffold sets `stop_runs: []`, uses no transcript and names no backup
remote. A real instance must deliberately configure its own evidence and backup.

[Validation](HARNESS-VALIDATION.md) records what ran locally and what remains
unverified. In particular, the historical live session did not show PostToolUse
feedback in 34 calls; synthetic hook tests do not close that observation gap.
