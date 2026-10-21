---
id: plugin-field.data
kind: plugin-field
status: VERIFIED
title: "data//"
sources: [S49]
---

# data//

**Sources:** [S49](src.s49.md)

The plugin's persistent directory, exposed as `${CLAUDE_PLUGIN_DATA}`. For how `` is formed, see Path variables and persistent data. Claude Code creates it when a plugin component first uses it and keeps it across updates. By default, Claude Code deletes it when you uninstall the plugin from its last scope. For `--keep-data` and the other cases where it stays, see plugin uninstall
