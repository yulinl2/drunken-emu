---
id: plugin.plugin-sources
kind: plugin
status: VERIFIED
title: "Plugin sources"
sources: [S51]
---

# Plugin sources

**Sources:** [S51](src.s51.md)

A plugin entry's `source` says where Claude Code fetches that one plugin from. It's either a relative path string or an object whose own `source` key names the type, so an entry looks like `"source": { "source": "github", "repo": "your-org/formatter" }`.
