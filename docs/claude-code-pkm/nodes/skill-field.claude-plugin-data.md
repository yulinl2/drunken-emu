---
id: skill-field.claude-plugin-data
kind: skill-field
status: VERIFIED
title: "${CLAUDE_PLUGIN_DATA}"
sources: [S32]
---

# ${CLAUDE_PLUGIN_DATA}

**Sources:** [S32](src.s32.md)

The plugin's persistent data directory, which survives plugin updates. Substituted only in plugin skills. Use this to reference installed dependencies, generated files, or caches that must outlive an update.
