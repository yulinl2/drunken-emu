---
id: feature.prompt-caching-in-a-fan-out
kind: feature
status: VERIFIED
title: "Prompt caching in a fan-out"
sources: [S29]
---

# Prompt caching in a fan-out

**Sources:** [S29](src.s29.md)

Agents in the same run can read each other's prompt cache. Two agents that run with the same model, effort level, agent type, tools, output schema, and working directory build the same tools-and-system-prompt prefix, so an agent that starts after a matching sibling's response has begun reads that sibling's cache on its first request.
