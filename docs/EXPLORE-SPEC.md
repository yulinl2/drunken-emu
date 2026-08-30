# `explore` — spec

Status: **design settled, not implemented**. Tracked as P1 in
`docs/OPEN-PROBLEMS.md`.

## The requirement this comes from

Long recursive click chains. Each step carries a stated intention. Intentions
are formed from common sense *and* from what is visible on the rendered page.
As close to a live person as possible.

## Why "a competent agent" is the wrong target

The obvious implementation — give an agent a goal, let it observe and act in a
loop — is a **worse** proxy for a real reader than it looks, because a competent
agent:

- scans the whole page patiently, finding entry points a real reader never sees
- remembers every path already tried, so it never loops
- persists through friction that would make a person quit

It would therefore **pass artifacts that real readers fail**. False negatives on
exactly the defects worth catching.

The three candidate models, by failure direction:

| model | failure |
|---|---|
| `blind_audit` (built) | **under**-powered — no intention, so it cannot test whether a goal is reachable at all |
| naive `explore` (rejected) | **over**-powered — patient and competent, silently passes bad design |
| **impaired `explore`** (this spec) | calibrated — has intentions, but the intentions degrade |

The repo's name is the spec, not a joke. Viewed from outside, impaired executive
function and drunkenness present alike: attention jumps, working memory leaks,
inhibition fails, the thread of the task is dropped mid-way. Modelling that is
the point. An artifact that survives a drunk emu survives everyone.

## Shape

```
bin/emu explore ARTIFACT.jsx --goal "find how to change the units" [flags]
```

Per step:

1. observe — screenshot + accessibility tree. **Never the `.jsx` source.**
   This is what preserves the half of the anti-leak rule that was always
   correct: the agent is content-blind because it only sees what a reader sees,
   not because it lacks goals.
2. decide — model call returns `{intention, action, target, rationale}`
3. act — Playwright executes it
4. record — append to the trace
5. loop until the goal is met, the budget is spent, or the run gives up

## Impairment parameters

The novel part. Each is a knob, and the point of the tool is sweeping them.

| flag | models | expected effect |
|---|---|---|
| `--working-memory N` | only the last N steps are visible to the decider | revisits paths already tried |
| `--distractibility p` | per step, probability p that the most salient element hijacks the choice | goal drift |
| `--patience k` | abandon after k steps of no progress | mid-task quitting |
| `--impulsivity` | act before the observation is fully consumed (truncate the a11y tree) | mistaps, skipped instructions |
| `--salience-driven` | rank candidates by contrast/size/motion instead of relevance | big ugly things beat correct things |

Defaults should be a *moderate* impairment profile, not zero. Zero impairment is
the rejected naive agent and should require asking for it explicitly.

## Output: a dose–response curve, not a boolean

Sweep the impairment level, run k trials per level, report goal-achievement
rate. The deliverable is the curve, and the summary statistic is the impairment
level at which achievement crosses 50%.

```
goal achieved
 1.0 ┤●●●●
     │    ●●●
 0.5 ┤ ─ ─ ─ ─●●─ ─ ─ ─   <- crossing point = the headline number
     │          ●●●
 0.0 ┤             ●●●●
     └──────────────────────
      0     impairment →    1
```

Why this shape matters:

- **comparable across revisions** — a redesign that shifts the curve right is
  better, and by a measurable amount. Pass/fail gives you none of that.
- **it is a survival curve**, so the whole standard toolkit applies: confidence
  bands, censoring for runs that hit the step budget without resolving,
  comparison of two curves as a two-sample problem.
- **it degrades honestly** — an artifact that only works for an unimpaired
  reader shows a cliff near zero, which is exactly the finding you want.

## Cost and placement

One model call per step, so a swept run is many calls. This is paid, and it is
non-deterministic. Consequences, both load-bearing:

- `explore` **cannot** be the CI gate. `blind_audit` stays as the free
  deterministic layer and `checks/ci_claims.py` stays as the README guard.
- `explore` runs are experiments and should be recorded as such — seed, model
  version, parameter vector, date — because the numbers are not reproducible
  across model versions.

## What must not happen to this spec

It has already been weakened once, by an argument that sounded right. If a
future session finds itself concluding that intentions are unnecessary, that
impairment can be dropped for simplicity, or that a fixed tap sequence is "close
enough" — that is the same failure recurring. Check it against README's
`## Falsified` row 3 before acting.
