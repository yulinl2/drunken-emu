---
id: feature.span-hierarchy
kind: feature
status: VERIFIED
title: "Span hierarchy"
sources: [S65]
---

# Span hierarchy

**Sources:** [S65](src.s65.md)

Each user prompt starts a `claude_code.interaction` root span. API calls, tool calls, and hook executions are recorded as its children. Tool spans have two child spans of their own: one for the time spent waiting on a permission decision and one for the execution itself. When the Agent tool, or legacy Task tool, spawns a subagent, the subagent's API and tool spans nest under the parent's `claude_c
