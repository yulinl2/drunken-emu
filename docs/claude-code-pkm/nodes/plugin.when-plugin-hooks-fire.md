---
id: plugin.when-plugin-hooks-fire
kind: plugin
status: VERIFIED
title: "When plugin hooks fire"
sources: [S45]
---

# When plugin hooks fire

**Sources:** [S45](src.s45.md)

A plugin's hooks don't wait for one of the plugin's skills or commands to be used. Claude Code registers them when a session loads the plugin, and they fire on their events from then on. To limit when a hook runs, narrow its `matcher`.
