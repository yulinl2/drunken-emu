---
id: plugin-field.name-plugins-marketplace-reference
kind: plugin-field
status: VERIFIED
title: "name"
sources: [S51]
---

# name

**Sources:** [S51](src.s51.md)

Marketplace identifier: letters, digits, `.`, `_`, and `-`, starting with a letter or digit, and no `..`. `claude plugin validate` fails any other name, because Claude Code can't install plugins from a marketplace that uses one. Users type the name after `@` in a plugin id such as `my-plugin@my-marketplace` when they install a plugin. See Reserved names (type: string)
