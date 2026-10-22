---
id: feature.api-errors-in-subagents
kind: feature
status: VERIFIED
title: "API errors in subagents"
sources: [S25]
---

# API errors in subagents

**Sources:** [S25](src.s25.md)

When something cuts off a subagent's response mid-stream, and the partial response contains text but no tool calls, Claude Code prompts the subagent to continue rather than ending the run. This happens in interactive sessions too. The run ends on the error only once those continuations are used up.
