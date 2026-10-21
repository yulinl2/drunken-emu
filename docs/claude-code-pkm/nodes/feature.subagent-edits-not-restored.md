---
id: feature.subagent-edits-not-restored
kind: feature
status: VERIFIED
title: "Subagent edits not restored"
sources: [S84]
---

# Subagent edits not restored

**Sources:** [S84](src.s84.md)

A subagent makes edits with Claude's file editing tools, but Claude Code usually doesn't capture those edits in your session's checkpoints. Whether rewinding restores them depends on how the subagent runs:
