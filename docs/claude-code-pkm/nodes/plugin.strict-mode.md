---
id: plugin.strict-mode
kind: plugin
status: VERIFIED
title: "Strict mode"
sources: [S51]
---

# Strict mode

**Sources:** [S51](src.s51.md)

`strict` decides what happens when the fetched plugin has its own `plugin.json` and the entry also declares any of the component fields: `commands`, `agents`, `skills`, `hooks`, `outputStyles`, or `themes`. With `strict: true`, the default, Claude Code appends the entry's component fields to `plugin.json`, except `hooks`, whose matchers replace the manifest's per event. With `strict: false`, an en
