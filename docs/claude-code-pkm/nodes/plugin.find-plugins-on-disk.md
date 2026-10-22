---
id: plugin.find-plugins-on-disk
kind: plugin
status: VERIFIED
title: "Find plugins on disk"
sources: [S49]
---

# Find plugins on disk

**Sources:** [S49](src.s49.md)

Claude Code keeps plugin files and state records under one plugins root, which is `~/.claude/plugins` unless you set `CLAUDE_CODE_PLUGIN_CACHE_DIR`. Every path in the table is relative to that root.
