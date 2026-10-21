---
id: feature.plugin-loaded-event
kind: feature
status: VERIFIED
title: "Plugin loaded event"
sources: [S65]
---

# Plugin loaded event

**Sources:** [S65](src.s65.md)

Logged once per enabled plugin at session start. Use this event to inventory which plugins are active across your fleet, as a complement to `plugin_installed` which records the install action itself.
