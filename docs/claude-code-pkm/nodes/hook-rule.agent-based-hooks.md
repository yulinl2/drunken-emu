---
id: hook-rule.agent-based-hooks
kind: hook-rule
status: VERIFIED
title: "Agent-based hooks"
sources: [S85]
---

# Agent-based hooks

**Sources:** [S85](src.s85.md)

Agent-based hooks (`type: "agent"`) are like prompt-based hooks but with multi-turn tool access. Instead of a single LLM call, an agent hook spawns a subagent that can read files, search code, and inspect the codebase to verify conditions. Agent hooks support the same events as prompt-based hooks, except `PermissionRequest`.
