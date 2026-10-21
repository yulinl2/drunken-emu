---
id: process.subagent-permission-routing
kind: process
status: VERIFIED
title: "Subagent permission routing"
sources: [S6]
---

# Subagent permission routing

**Sources:** [S6](src.s6.md)

Launching a subagent does not prompt by itself; the subagent's own tool calls are checked against the permission rules. Foreground subagents show prompts in place. Background subagents send them to the main session, where Esc denies one call. See [Agent](tool.agent.md).
