---
id: feature.run-a-shell-command
kind: feature
status: VERIFIED
title: "Run a shell command"
sources: [S26]
---

# Run a shell command

**Sources:** [S26](src.s26.md)

To run a shell command as a background job instead of a Claude session, pass `--exec`. The following example runs `pytest -x` as a background job:
