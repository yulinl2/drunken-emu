---
id: feature.values-and-warnings-for-claude-code-auto-compact-window
kind: feature
status: VERIFIED
title: "Values and warnings for CLAUDE_CODE_AUTO_COMPACT_WINDOW"
sources: [S70]
---

# Values and warnings for CLAUDE_CODE_AUTO_COMPACT_WINDOW

**Sources:** [S70](src.s70.md)

A warning that quotes your `CLAUDE_CODE_AUTO_COMPACT_WINDOW` value means the value falls outside 100,000 to 1,000,000 or isn't a token count. To stop the warning, set a number in that range, such as `CLAUDE_CODE_AUTO_COMPACT_WINDOW=200000`. On Claude Code v2.1.304 or later, you can also write the number with `k` for thousands or `M` for millions, as in `200k` or `1M`.
