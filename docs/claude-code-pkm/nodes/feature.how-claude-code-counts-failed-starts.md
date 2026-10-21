---
id: feature.how-claude-code-counts-failed-starts
kind: feature
status: VERIFIED
title: "How Claude Code counts failed starts"
sources: [S75]
---

# How Claude Code counts failed starts

**Sources:** [S75](src.s75.md)

Sessions that count: only sessions that started in fullscreen rendering because your `tui` setting says so, because you accepted the startup dialog, or because Claude Code starts you in fullscreen by default `CLAUDE_CODE_NO_FLICKER=1`: if you set it, Claude Code renders that session fullscreen even after a failed start, and doesn't count it
