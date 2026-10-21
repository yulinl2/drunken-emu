---
id: hook-rule.output-top-level-block
kind: hook-rule
status: VERIFIED
title: "Output: top-level block"
sources: [S2]
---

# Output: top-level block

**Sources:** [S2](src.s2.md)

A top-level decision of block is honored on UserPromptSubmit, UserPromptExpansion, PostToolUse, PostToolUseFailure, PostToolBatch, Stop, SubagentStop, ConfigChange and PreCompact. On TaskCreated it cancels the task.

## Linked from

- [UserPromptSubmit](hook.user-prompt-submit.md)
