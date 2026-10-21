---
id: hook-rule.exit-2-blocks
kind: hook-rule
status: VERIFIED
title: "Exit code 2: blocking events"
sources: [S2]
---

# Exit code 2: blocking events

**Sources:** [S2](src.s2.md)

On events that can block, exit 2 blocks, and stderr is the reason unless the JSON supplies one. Events: PreToolUse, UserPromptSubmit, UserPromptExpansion, PreModelSwitch, PreCompact, Stop, SubagentStop, TeammateIdle, TaskCreated, TaskCompleted, ConfigChange (except policy settings), PostToolBatch, Elicitation, ElicitationResult, WorktreeCreate and WorktreeRemove.
