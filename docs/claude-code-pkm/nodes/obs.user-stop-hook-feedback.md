---
id: obs.user-stop-hook-feedback
kind: observation
status: REPO
title: "Observation: user-level Stop hook reached the model"
sources: [S9]
---

# Observation: user-level Stop hook reached the model

**Sources:** [S9](src.s9.md)

A user-level Stop hook outside the repo (~/.claude/stop-hook-git-check.sh) ran at the end of a turn. Its exit-2 stderr reached the model as "Stop hook feedback" (SANDBOX-FACTS, 2026-10-17). See [Stop](hook.stop.md).
