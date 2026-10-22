---
id: env.claude-agent-sdk-disable-builtin-agents
kind: env
status: VERIFIED
title: "CLAUDE_AGENT_SDK_DISABLE_BUILTIN_AGENTS"
sources: [S81]
---

# CLAUDE_AGENT_SDK_DISABLE_BUILTIN_AGENTS

**Sources:** [S81](src.s81.md)

Set to `1` to disable all built-in subagent types such as Explore and Plan. Only applies in non-interactive mode (the `-p` flag). Useful for SDK users who want a blank slate. This also removes `general-purpose`, the subagent Claude Code runs when an Agent tool call omits `subagent_type`. Such a call then fails with `subagent_type is required`
