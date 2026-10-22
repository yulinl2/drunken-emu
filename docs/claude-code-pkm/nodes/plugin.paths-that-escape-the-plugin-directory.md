---
id: plugin.paths-that-escape-the-plugin-directory
kind: plugin
status: VERIFIED
title: "Paths that escape the plugin directory"
sources: [S49]
---

# Paths that escape the plugin directory

**Sources:** [S49](src.s49.md)

Whether a plugin loads in place or from a cached copy, Claude Code doesn't let it declare components outside its own directory. It rejects a component path that resolves outside the plugin root, whether the path is declared in `plugin.json` or in a marketplace entry:
