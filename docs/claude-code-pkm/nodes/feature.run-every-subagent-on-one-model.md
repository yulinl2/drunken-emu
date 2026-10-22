---
id: feature.run-every-subagent-on-one-model
kind: feature
status: VERIFIED
title: "Run every subagent on one model"
sources: [S25]
---

# Run every subagent on one model

**Sources:** [S25](src.s25.md)

`CLAUDE_CODE_SUBAGENT_MODEL` is a default, so a subagent's definition or a model Claude passes still takes precedence over it. To apply one model to every subagent, teammate, and workflow agent, also set `CLAUDE_CODE_SUBAGENT_MODEL_FORCE` to `1`. Requires Claude Code v2.1.257 or later.
