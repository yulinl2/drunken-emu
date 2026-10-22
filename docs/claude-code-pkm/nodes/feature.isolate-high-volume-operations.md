---
id: feature.isolate-high-volume-operations
kind: feature
status: VERIFIED
title: "Isolate high-volume operations"
sources: [S25]
---

# Isolate high-volume operations

**Sources:** [S25](src.s25.md)

One of the most effective uses for subagents is isolating operations that produce large amounts of output. Running tests, fetching documentation, or processing log files can consume significant context. By delegating these to a subagent, the verbose output stays in the subagent's context while only the relevant summary returns to your main conversation.
