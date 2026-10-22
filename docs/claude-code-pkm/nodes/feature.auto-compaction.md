---
id: feature.auto-compaction
kind: feature
status: VERIFIED
title: "Auto-compaction"
sources: [S25]
---

# Auto-compaction

**Sources:** [S25](src.s25.md)

Subagents support automatic compaction. Compaction triggers as the subagent's own context window fills, and `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` applies to subagents as well. See environment variables for when the override takes effect.
