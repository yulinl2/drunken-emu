---
id: plugin.cleanup-of-previous-versions
kind: plugin
status: VERIFIED
title: "Cleanup of previous versions"
sources: [S49]
---

# Cleanup of previous versions

**Sources:** [S49](src.s49.md)

When you update or uninstall a plugin, Claude Code writes an `.orphaned_at` marker into the previous version directory. It removes that directory in a background cleanup 14 days later, so a session that already loaded the old version keeps running.
