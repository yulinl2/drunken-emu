---
id: feature.plugin-components-that-keep-the-cache
kind: feature
status: VERIFIED
title: "Plugin components that keep the cache"
sources: [S18]
---

# Plugin components that keep the cache

**Sources:** [S18](src.s18.md)

Claude Code never invalidates the cache for a plugin's skills, commands, agents, hooks, monitors, or themes. It appends their content after the existing conversation, so the next request pays for that content and still reads everything before it from the cache.
