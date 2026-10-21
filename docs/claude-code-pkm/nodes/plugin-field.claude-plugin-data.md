---
id: plugin-field.claude-plugin-data
kind: plugin-field
status: VERIFIED
title: "${CLAUDE_PLUGIN_DATA}"
sources: [S50]
---

# ${CLAUDE_PLUGIN_DATA}

**Sources:** [S50](src.s50.md)

resolves to: `~/.claude/plugins/data//`, created on first reference and kept across plugin updates. `` is the plugin identifier with every character other than a letter, digit, `_`, or `-` replaced by `-`; use it for: Installed dependencies such as `node_modules`, generated code, and caches
