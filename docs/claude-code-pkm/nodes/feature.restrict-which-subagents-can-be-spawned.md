---
id: feature.restrict-which-subagents-can-be-spawned
kind: feature
status: VERIFIED
title: "Restrict which subagents can be spawned"
sources: [S25]
---

# Restrict which subagents can be spawned

**Sources:** [S25](src.s25.md)

When an agent runs as the main thread with `claude --agent`, it can spawn subagents using the Agent tool. To restrict which subagent types it can spawn, use `Agent(agent_type)` syntax in the `tools` field.
