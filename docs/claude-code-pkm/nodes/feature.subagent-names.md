---
id: feature.subagent-names
kind: feature
status: VERIFIED
title: "Subagent names"
sources: [S25]
---

# Subagent names

**Sources:** [S25](src.s25.md)

If you start a session with agent teams enabled, Claude can give a subagent a name by passing a `name` parameter on the Agent tool call. It may do so on its own, without asking you first. The name makes the subagent addressable: Claude can message or resume it by name after it finishes.
