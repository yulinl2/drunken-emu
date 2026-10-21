---
id: plugin-field.inline
kind: plugin-field
status: VERIFIED
title: "@inline"
sources: [S49]
---

# @inline

**Sources:** [S49](src.s49.md)

how the plugin got there: You started Claude Code with `--plugin-dir` or `--plugin-url`, set `CLAUDE_CODE_PLUGIN_DIRS`, or an Agent SDK app passed the `plugins` option. It loads for that session only; how you turn it on or off: On for the session unless the manifest sets `defaultEnabled: false` or a settings file sets `"@inline": false`
