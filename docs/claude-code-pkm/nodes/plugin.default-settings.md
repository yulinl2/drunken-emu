---
id: plugin.default-settings
kind: plugin
status: VERIFIED
title: "Default settings"
sources: [S45]
---

# Default settings

**Sources:** [S45](src.s45.md)

To set defaults that apply while the plugin is enabled, add a `settings.json` at the plugin root, or put the same object inline in the `settings` manifest key. Two keys take effect, `agent` and `subagentStatusLine`, and every other key is dropped.
