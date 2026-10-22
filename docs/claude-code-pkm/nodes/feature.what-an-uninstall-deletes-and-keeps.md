---
id: feature.what-an-uninstall-deletes-and-keeps
kind: feature
status: VERIFIED
title: "What an uninstall deletes and keeps"
sources: [S52]
---

# What an uninstall deletes and keeps

**Sources:** [S52](src.s52.md)

When you uninstall a plugin from the last scope it's installed at, Claude Code also deletes the plugin's stored options and secrets and its data directory, `~/.claude/plugins/data//`. There are three exceptions:
