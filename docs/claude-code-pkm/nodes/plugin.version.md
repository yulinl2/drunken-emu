---
id: plugin.version
kind: plugin
status: VERIFIED
title: "version"
sources: [S50]
---

# version

**Sources:** [S50](src.s50.md)

A version string, not checked against semver. Setting it pins the plugin to that version until you change it; see Versions and updates. A plugin with a `command` source, a plugin from a marketplace hosted on claude.ai, and a plugin loaded in place from a marketplace added from a local path aren't pinned by this field.
