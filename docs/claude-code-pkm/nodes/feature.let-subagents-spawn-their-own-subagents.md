---
id: feature.let-subagents-spawn-their-own-subagents
kind: feature
status: VERIFIED
title: "Let subagents spawn their own subagents"
sources: [S25]
---

# Let subagents spawn their own subagents

**Sources:** [S25](src.s25.md)

By default, a subagent can spawn subagents of its own, up to three layers below the main conversation. At the depth limit, Claude Code withholds the `Agent` tool from every subagent except a fork, so a subagent at the limit does its delegated work itself and returns one summary. A fork at the limit keeps `Agent` in its inherited tool list, but the tool returns an error instead of spawning.
