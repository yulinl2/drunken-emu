---
id: dec.d10
kind: decision
status: DECIDED
title: "D10: Commit on top of main"
sources: [S8]
---

# D10: Commit on top of main

**Sources:** [S8](src.s8.md)

Before any edit, the designated branch matched main and its origin copy, and the commit-range checks were empty. Stacking on merged history is forbidden ([Never rewrite history](git-rule.no-history-rewrite.md)), and this branch had no merged history.
