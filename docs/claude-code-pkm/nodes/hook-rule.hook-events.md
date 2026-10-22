---
id: hook-rule.hook-events
kind: hook-rule
status: VERIFIED
title: "Hook events"
sources: [S85]
---

# Hook events

**Sources:** [S85](src.s85.md)

Each event corresponds to a point in Claude Code's lifecycle where hooks can run. The sections below are ordered to match the lifecycle: from session setup through the agentic loop to session end. Each section describes when the event fires, what matchers it supports, the JSON input it receives, and how to control behavior through output.
