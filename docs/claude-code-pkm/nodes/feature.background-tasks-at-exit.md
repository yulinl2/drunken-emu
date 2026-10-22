---
id: feature.background-tasks-at-exit
kind: feature
status: VERIFIED
title: "Background tasks at exit"
sources: [S38]
---

# Background tasks at exit

**Sources:** [S38](src.s38.md)

After Claude finishes its turn and stdin has closed, a `claude -p` run can stay open to wait for background work that Claude started.
