# Directory tree index

*v0.2.0 · 2026-08-31 · generated, CI-asserted*

Canonical copy of the tracked file set. The README carries a **curated** subset
with one-line annotations for landing readers; that one is deliberately partial
and is not generated. This one is exact.

Source of truth is `git ls-files`, so the tree means precisely *what a clone
receives*. Untracked working files (`out/*.png`, `harness/app.jsx`, `__pycache__`)
are absent by construction rather than by an exclusion list that can go stale.

```
python3 bin/gen_tree.py --write     # regenerate this block
python3 bin/gen_tree.py --check     # exit 1 on drift; runs in CI
```

*Why generated:* until v0.2.0 this file carried the command
`tree -I 'out|__pycache__|.git' --dirsfirst`, which **cannot** produce the
content that sat below it — `tree` hides dotfiles without `-a`, so `.github/`
and `.gitignore` were invisible to it, and nothing compared the two. The index
drifted through three commits before anyone re-ran it. A regeneration command
that is never executed is not a regeneration command.

```text
.
|-- .claude/
|   `-- settings.json
|-- .github/
|   `-- workflows/
|       `-- claims.yml
|-- bin/
|   |-- apply_doi.sh
|   |-- blocker_check.py
|   |-- emu
|   |-- figpipe
|   |-- gen_tree.py
|   `-- sync_artifact.py
|-- checks/
|   |-- fixtures/
|   |   |-- chains/
|   |   |   |-- hw1_correction_pass.json
|   |   |   |-- hw1_correction_pass_fixed.json
|   |   |   `-- worked_example.json
|   |   |-- fragment_links_clean.jsx
|   |   |-- fragment_links_nolinks.jsx
|   |   `-- fragment_links_planted.jsx
|   |-- __init__.py
|   |-- affordances.py
|   |-- blind_audit.py
|   |-- browser.py
|   |-- chain.py
|   |-- chain_check.py
|   |-- chain_load.py
|   |-- chain_verifiers.py
|   |-- ci_claims.py
|   |-- explore_run.py
|   |-- explore_step.py
|   |-- explore_text.py
|   |-- fragment_links.py
|   |-- region_shots.py
|   |-- smoke.py
|   |-- svg_legibility.py
|   |-- svg_text_gates.py
|   |-- test_chain.py
|   |-- test_explore_run.py
|   |-- test_explore_text.py
|   |-- test_external_svg.py
|   `-- test_fragment_links.py
|-- docs/
|   |-- EXPLORE-SPEC.md
|   |-- LATEST-CONCLUSIONS.md
|   |-- OPEN-PROBLEMS.md
|   |-- OPERATION-CHAINS.md
|   |-- OPERATION-MODEL.md
|   |-- SANDBOX-FACTS.md
|   |-- TREE.md
|   `-- ZENODO-RUNBOOK.md
|-- figbank/
|   |-- app/
|   |   |-- frontier-tree/
|   |   |   |-- src/
|   |   |   |   |-- App.tsx
|   |   |   |   |-- Figure.tsx
|   |   |   |   |-- data.ts
|   |   |   |   |-- index.css
|   |   |   |   `-- main.tsx
|   |   |   |-- .gitignore
|   |   |   |-- .parcelrc
|   |   |   |-- .postcssrc
|   |   |   |-- README.md
|   |   |   |-- check_page.py
|   |   |   |-- index.html
|   |   |   |-- package.json
|   |   |   |-- pnpm-lock.yaml
|   |   |   |-- tailwind.config.js
|   |   |   |-- tsconfig.app.json
|   |   |   |-- tsconfig.json
|   |   |   |-- tsconfig.node.json
|   |   |   `-- vite.config.ts
|   |   |-- variable-model/
|   |   |   |-- src/
|   |   |   |   |-- App.tsx
|   |   |   |   |-- Figure.tsx
|   |   |   |   |-- data.ts
|   |   |   |   |-- index.css
|   |   |   |   `-- main.tsx
|   |   |   |-- .gitignore
|   |   |   |-- .parcelrc
|   |   |   |-- .postcssrc
|   |   |   |-- README.md
|   |   |   |-- check_page.py
|   |   |   |-- index.html
|   |   |   |-- package.json
|   |   |   |-- pnpm-lock.yaml
|   |   |   |-- tailwind.config.js
|   |   |   |-- tsconfig.app.json
|   |   |   |-- tsconfig.json
|   |   |   |-- tsconfig.node.json
|   |   |   `-- vite.config.ts
|   |   `-- bundle.sh
|   |-- examples/
|   |   |-- figbank-file-tree.json
|   |   |-- figbank-file-tree.pdf
|   |   |-- figbank-file-tree.png
|   |   |-- figbank-file-tree.svg
|   |   |-- gen_file_tree.py
|   |   |-- gen_majority_vote.py
|   |   |-- majority-vote-curve.json
|   |   |-- majority-vote-curve.pdf
|   |   |-- majority-vote-curve.png
|   |   |-- majority-vote-curve.svg
|   |   |-- pipeline-sequence.json
|   |   |-- pipeline-sequence.pdf
|   |   |-- pipeline-sequence.png
|   |   |-- pipeline-sequence.svg
|   |   |-- pipeline-workflow.json
|   |   |-- pipeline-workflow.png
|   |   |-- pipeline-workflow.svg
|   |   |-- round-lifecycle.json
|   |   |-- round-lifecycle.pdf
|   |   |-- round-lifecycle.png
|   |   |-- round-lifecycle.svg
|   |   `-- verdicts.jsonl
|   |-- lib/
|   |   |-- components.js
|   |   |-- figure.d.ts
|   |   |-- figure.js
|   |   |-- lifecyclelayout.js
|   |   |-- palette.d.ts
|   |   |-- palette.js
|   |   |-- plot.js
|   |   |-- plotlayout.js
|   |   |-- sequencelayout.js
|   |   |-- text.js
|   |   |-- treelayout.js
|   |   |-- vnode.d.ts
|   |   `-- vnode.js
|   |-- reader/
|   |   `-- cold-reader.md
|   |-- schema/
|   |   `-- figure.schema.json
|   |-- tests/
|   |   |-- calibration.json
|   |   |-- figure.test.js
|   |   |-- fixture-two-regions.json
|   |   |-- plot.test.js
|   |   `-- text.test.js
|   |-- README.md
|   |-- package.json
|   `-- render_svg.js
|-- harness/
|   `-- harness.html
|-- out/
|   `-- .gitkeep
|-- vendor/
|   |-- babel.js
|   |-- react.js
|   |-- reactdom.js
|   `-- tailwind.js
|-- .gitignore
|-- CITATION.cff
|-- CLAUDE.md
|-- CONTRIBUTING.md
|-- LICENSE
|-- Makefile
|-- NOTICE
|-- README.md
`-- THIRD_PARTY_NOTICES.md

22 directories, 141 files tracked
```
