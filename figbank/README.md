# figbank — a figure is composed from a spec, not drawn; accepted by a blind reader, not by its author

*v0.1.0 · 2026-09-28 · the visual-instruments track (issue #5); first instances MetaProof fig4 and fig5*

The kit's contract, extended from React artifacts and static SVGs to *making* figures: the brief is
machine-readable, the picture is composed from reusable pieces, the same pieces render to SVG for
LaTeX and to React for pages, and a figure is accepted only when a reader who has seen nothing but
the PNG can say what it claims. The acceptance is a record (`verdicts.jsonl`), not a chat.

```
figbank/
├── schema/figure.schema.json   one JSON schema for "a figure": message, regions, symbols, arrows,
│                               status tags, word budget, acceptance rule
├── lib/                        the component bank (plain ES modules, no dependencies)
│   ├── vnode.js                one tree, two hosts: h() → toSvg() | toReact()
│   ├── text.js                 width estimate calibrated against Chromium (tests/calibration.json), wrap()
│   ├── palette.js              LIGHT / DARK palettes; status → mark (dot, square, hollow)
│   ├── components.js           region · itemList · chipFlow · functional · arrow · note · frame · legend ·
│   │                           treeNode · treeEdge
│   ├── treelayout.js           a tree's x/y from nothing but parent pointers; vertical or horizontal
│   └── figure.js               renderFigure(spec) → {node, svg, report}; the gates live here; `boundaries`
│                               (a labelled group computed around named region ids) and `tree` too
├── render_svg.js               node CLI: spec.json → figure.svg (+ report)
├── reader/cold-reader.md       the blind reader's prompt; its hash is in every verdict
├── app/
│   ├── bundle.sh               Parcel + html-inline → one HTML shell with a __JSON__ data slot
│   └── variable-model/         the MetaProof variable-model page (React + TS + Tailwind); imports lib/
│       └── check_page.py       the page's function checklist, run by a script reader in Chromium
├── examples/                   specs that document the bank's own tooling, not a consumer's model
│   ├── pipeline-workflow.json  bin/figpipe's own seven steps, as a `boundaries` demo
│   └── figbank-file-tree.json  figbank/'s own tracked files, as a `tree` demo (gen_file_tree.py)
└── tests/                      node --test: gates, React host, calibration, tree layout
bin/figpipe                     the pipeline: validate → render → rasterise → legibility → cold read → accept → log
```

## The gates (what the renderer refuses)

A figure fails before any reader sees it when: a box's items do not fit (nothing truncates — a symbol
wraps, and if it still does not fit the region reports overflow); the running text (title, arrow
labels, legend, notes) exceeds `word_budget`; a `must_not_contain` string is present; an ellipsis is
present anywhere. Symbols, names and region titles are labels and are not counted.

## Boundaries — grouping regions for a *process*, not a data model

`spec.boundaries: [{label, wraps: [region-ids], color, pad}]` draws a labelled dashed frame behind the
regions it names, sized to their union plus `pad` — the box is computed, never hand-placed, so it can't
drift from the regions it groups. This is the one pattern worth taking from `tt-a1i/archify` (a
schema-validated, explicit-coordinate diagramming skill with the same "layout judgment over
auto-layout" stance): a figure that explains a *process* — these steps are mechanical, this one is
judgment — needs grouping that a plain region/arrow figure (built for "every variable has one box")
does not. `figbank/examples/pipeline-workflow.json` demonstrates it on the bank's own pipeline and
passed the blind reader clear on the first round: "a tool ... runs it through four automatic technical
checks, then a separate blind human-like judgment step, with the outcome recorded in a log."

Archify's five diagram kinds (architecture, workflow, sequence, dataflow, lifecycle) are otherwise a
different tool for a different job — an ad-hoc CLI that authors a fresh diagram per request from a
description, not a bank that regenerates the same figure from the same versioned source every time —
so it is not a dependency here. A `sequence` kind (participants + a timeline of messages) and a
`lifecycle` kind (states + transitions) would be the next genuinely new component types if a consumer
needs them; nothing in the schema or renderer assumes them yet.

## Trees — visualizing structure that already exists in the repos, not just illustrating a model

`spec.tree: {nodes: [{id, parent, label, status?}], origin, node_w, node_h, gap_x, gap_y, orientation}`.
`treelayout.js` computes every position from nothing but each node's `parent` (bottom-up subtree size,
a node centred over its own children — overlap-free for any tree, not full Reingold–Tilford tidying);
`orientation: "horizontal"` grows depth rightward and stacks siblings top-to-bottom, which almost every
real tree in these repos wants (a directory tree, MetaProof's problem tree) because they are wide-but-
shallow, not deep-but-narrow — `vertical` is the other shape, depth downward, siblings side by side.
An unreachable node (a parent cycle) is a thrown error, never a silently vanished node.

Owner's prompt for this (2026-09-28 chat, drunken-emu #11): every tree/DAG already in these repos is a
visualization candidate, and the picture might show something a reader — human or agent — had not
noticed, the way MetaProof treats reader/builder/user as one loop. First instance, proof before spending
the primitive on a harder one: `figbank-file-tree.json`, the bank visualizing its own 49 tracked files,
regenerated by `examples/gen_file_tree.py`, accepted blind on the first round, verdict *clear*. Next,
tracked in #11: MetaProof's `ledgers/frontier.jsonl` (a clean 68-node single-parent tree; right now 35
measured, 0 sealed — the same imbalance `bin/frontier_refactor.py` already found numerically, C-722,
OP-32, which a status-coloured tree would make perceptually obvious) and MetaSci's `kb/claims-graph`
(a real DAG — multi-parent, needs cross-link routing this primitive does not attempt yet). Frontier's
node titles are full sentences, too long for 68 static boxes without truncating something the bank
refuses to truncate — the honest shape there is very likely a compact tree (id + status only) backed
by a click-for-detail panel, the variable-model page's own pattern, not a bigger print figure.

## The pipeline (`bin/figpipe SPEC.json --out DIR --reader auto`)

| step | tool | what the record carries |
|---|---|---|
| validate | jsonschema (or a structural subset) | errors |
| render | `render_svg.js` | words, budget, n_texts, render errors, SVG hash |
| rasterise | headless Chromium (`checks/browser.py` finds the installed one) | PNG at `--png-scale`, vector PDF sized to the viewBox |
| legibility | `checks/svg_legibility.py` at `acceptance.legibility` | min rendered font, faults |
| cold read | `claude -p --allowedTools Read`, the prompt file + the PNG path, nothing else | the report verbatim, cost, prompt hash |
| accept | `acceptance.must_mention` groups in claim+structure; `must_not_mention` absent; `unreadable` ≤ max; legibility passed | accepted, reasons, round |

`--reader none` stops after legibility (what a consumer's `make figures` runs); `--reader FILE` takes a
verdict produced elsewhere (a human, a subagent) so the acceptance is still mechanical.

The reader's "unreadable" is physical or structural only; unfamiliar terms go to "questions", which
are logged and never counted, because a blind reader by construction has no context. This split was
added after the first fixture run, where the reader filed "what Φ stands for" as unreadable.

## Measured, 2026-09-28 (this container)

- `claude -p` blind read of one PNG: 23–29 s, $0.06–0.08 per figure.
- fig5 of MetaProof: the matplotlib version (five equal boxes, 130 words of running text) got verdict
  *partly* with five unreadable items; the composed version (indented stack, 40 words) got *partly*
  with none, and the reader's claim was the brief's message in its own words. Round 1.
- fig4: round 1, unreadable empty; the reader wrote "terms" where the keyword proxy demanded
  "variable". The proxy was widened (`["variable", "term", "quantit", "symbol"]`) and the same blind
  read re-evaluated; both records are in MetaProof `figures/verdicts.jsonl`.
- Round 2 against the theory session's own briefs (MetaProof #51, requirements at the briefs' feet): fig4 with
  four named items a region and the channels drawn through the Interface, fig5 with J's three terms in words and no
  other formula — both accepted at round 2, unreadable empty, $0.07 each; the all-variables map (kept as
  `variable-map` for the page) accepted too. Three figures, one command, one record.
- The page shell: 252 KB, React 19 + Tailwind, no other runtime dependency; `check_page.py` passes
  all ten functions of the hand-written page it replaced, in light and dark.

## What is not done

fig1–fig3 of MetaProof are still matplotlib (no brief, no reader); talk frames and MetaSci / HAN figures
are not in the bank; a figure spec has explicit box coordinates, so a layout engine that places regions
from constraints is the next piece of leverage; the width estimate is per-character, not per-font, so a
figure that asks for a different face than DejaVu Sans should re-calibrate `tests/calibration.json`.
