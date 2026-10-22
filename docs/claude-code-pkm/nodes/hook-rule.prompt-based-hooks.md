---
id: hook-rule.prompt-based-hooks
kind: hook-rule
status: VERIFIED
title: "Prompt-based hooks"
sources: [S85]
---

# Prompt-based hooks

**Sources:** [S85](src.s85.md)

In addition to command, HTTP, and MCP tool hooks, Claude Code supports prompt-based hooks (`type: "prompt"`) that use an LLM to evaluate whether to allow or block an action, and agent hooks (`type: "agent"`) that spawn an agentic verifier with tool access. Not all events support every hook type.
