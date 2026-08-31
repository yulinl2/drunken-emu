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
|   |-- emu
|   |-- gen_tree.py
|   `-- sync_artifact.py
|-- checks/
|   |-- blind_audit.py
|   |-- ci_claims.py
|   |-- explore_step.py
|   |-- region_shots.py
|   `-- smoke.py
|-- docs/
|   |-- EXPLORE-SPEC.md
|   |-- LATEST-CONCLUSIONS.md
|   |-- OPEN-PROBLEMS.md
|   |-- SANDBOX-FACTS.md
|   |-- TREE.md
|   `-- ZENODO-RUNBOOK.md
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
|-- NOTICE
|-- README.md
`-- THIRD_PARTY_NOTICES.md

8 directories, 29 files tracked
```
