---
id: feature.subagent-completed-event
kind: feature
status: VERIFIED
title: "Subagent completed event"
sources: [S65]
---

# Subagent completed event

**Sources:** [S65](src.s65.md)

Logged when a subagent finishes and returns its result to the conversation that started it. Use it to roll up tool use and run time by subagent type; for token or cost rollups, use the token counter and cost counter filtered to `query_source` `"subagent"`, since this event's `total_tokens` covers only the final request. The `"subagent"` category also counts requests from agent-based hooks, which e
