---
id: feature.background-work-defers-evaluation
kind: feature
status: VERIFIED
title: "Background work defers evaluation"
sources: [S37]
---

# Background work defers evaluation

**Sources:** [S37](src.s37.md)

If a subagent or a background shell command is still running when a turn ends, Claude Code skips the evaluation for that turn. It evaluates at the end of the next turn that finishes with no background work running. When the background work finishes, Claude Code delivers the result to Claude as a new turn, so you don't have to prompt.
