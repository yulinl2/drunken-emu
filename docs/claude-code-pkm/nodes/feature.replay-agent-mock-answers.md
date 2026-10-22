---
id: feature.replay-agent-mock-answers
kind: feature
status: VERIFIED
title: "Replay agent mock answers"
sources: [S47]
---

# Replay agent mock answers

**Sources:** [S47](src.s47.md)

A `type: agent` mock answers with a call to the `--judge-model`, so its output varies between runs and changes if you change the judge. When a run completes without an error or abort, Claude Code saves each answer an agent mock gave under the results directory in `mock-recordings/`.
