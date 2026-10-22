---
id: feature.agent-type-not-found-for-one-of-your-plugin-s-agents
kind: feature
status: VERIFIED
title: "\"Agent type '...' not found\" for one of your plugin's agents"
sources: [S47]
---

# "Agent type '...' not found" for one of your plugin's agents

**Sources:** [S47](src.s47.md)

By default each case runs both with your plugin and without it, and the runs without it are the no-plugin baseline. When Claude dispatches one of your plugin's agents in a baseline run, the Agent tool call fails with `Agent type ':' not found. Available agents: ...`. The list names only agents that exist without the plugin, such as the built-in subagents.
