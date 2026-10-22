---
id: plugin.bare-names-under-pluginroot
kind: plugin
status: VERIFIED
title: "Bare names under pluginRoot"
sources: [S51]
---

# Bare names under pluginRoot

**Sources:** [S51](src.s51.md)

A bare name is a single directory name with no `/`, such as `"formatter"`. To write bare names instead of `./` paths, set `metadata.pluginRoot` to the directory they resolve under. With `"pluginRoot": "./plugins"`, `"source": "formatter"` resolves to `./plugins/formatter`. Requires Claude Code v2.1.239 or later.
