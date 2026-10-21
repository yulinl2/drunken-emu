---
id: hook-field.agent-type
kind: hook-field
status: VERIFIED
title: "agent_type"
sources: [S85]
---

# agent_type

**Sources:** [S85](src.s85.md)

Agent name (for example, `"Explore"` or `"security-reviewer"`). Present when the session uses `--agent` or the hook fires inside a subagent. For subagents, the subagent's type takes precedence over the session's `--agent` value. See SubagentStart for the values custom and plugin subagents report and how to write a matcher against a plugin-scoped name.
