---
id: env.claude-autocompact-pct-override
kind: env
status: VERIFIED
title: "CLAUDE_AUTOCOMPACT_PCT_OVERRIDE"
sources: [S81]
---

# CLAUDE_AUTOCOMPACT_PCT_OVERRIDE

**Sources:** [S81](src.s81.md)

Set the percentage (1-100) of the auto-compact window at which auto-compaction triggers. Use lower values like `50` to compact earlier; the variable can't raise the threshold, so values above the default percentage are ignored. It applies only in sessions that compact before the model's context limit. Applies to both main conversations and subagents
