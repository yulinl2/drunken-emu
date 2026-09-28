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
|-- .github/
|   `-- workflows/
|       `-- claims.yml
|-- bin/
|   |-- apply_doi.sh
|   |-- blocker_check.py
|   |-- emu
|   |-- figpipe
|   |-- gen_ledger.py
|   |-- gen_tree.py
|   `-- sync_artifact.py
|-- checks/
|   |-- __init__.py
|   |-- blind_audit.py
|   |-- browser.py
|   |-- ci_claims.py
|   |-- explore_step.py
|   |-- explore_text.py
|   |-- region_shots.py
|   |-- smoke.py
|   |-- svg_legibility.py
|   `-- test_explore_text.py
|-- docs/
|   |-- tutorial/
|   |   `-- SPINE.md
|   |-- EXPLORE-SPEC.md
|   |-- LATEST-CONCLUSIONS.md
|   |-- OPEN-PROBLEMS.md
|   |-- SANDBOX-FACTS.md
|   |-- TREE.md
|   `-- ZENODO-RUNBOOK.md
|-- figbank/
|   |-- app/
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
|   |   |-- pipeline-workflow.json
|   |   |-- pipeline-workflow.png
|   |   |-- pipeline-workflow.svg
|   |   `-- verdicts.jsonl
|   |-- lib/
|   |   |-- components.js
|   |   |-- figure.d.ts
|   |   |-- figure.js
|   |   |-- palette.d.ts
|   |   |-- palette.js
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
|   |   `-- text.test.js
|   |-- LEDGER.md
|   |-- README.md
|   |-- ledger.json
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
|-- CONTRIBUTING.md
|-- LICENSE
|-- Makefile
|-- NOTICE
|-- README.md
`-- THIRD_PARTY_NOTICES.md

18 directories, 87 files tracked
```
