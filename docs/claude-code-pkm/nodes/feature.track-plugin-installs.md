---
id: feature.track-plugin-installs
kind: feature
status: VERIFIED
title: "Track plugin installs"
sources: [S38]
---

# Track plugin installs

**Sources:** [S38](src.s38.md)

When `CLAUDE_CODE_SYNC_PLUGIN_INSTALL` is set, Claude Code emits `system/plugin_install` events while marketplace plugins install before the first turn. Use these to surface install progress in your own UI.
