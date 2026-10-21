---
id: plugin-field.name-plugins-marketplace-reference-2
kind: plugin-field
status: VERIFIED
title: "name"
sources: [S51]
---

# name

**Sources:** [S51](src.s51.md)

Plugin identifier: letters, digits, `.`, `_`, and `-`, starting with a letter or digit. `claude plugin validate` fails other names, which Claude Code can't install. Users type it before `@` when they install, even when the plugin's own `plugin.json` sets a different `name` (type: string)
