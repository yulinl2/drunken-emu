---
id: plugin-field.plugins-plugins-marketplace-reference
kind: plugin-field
status: VERIFIED
title: "plugins"
sources: [S51]
---

# plugins

**Sources:** [S51](src.s51.md)

The inline catalog, with no hosted file. Each item takes `name`, `source`, `description`, `version`, `strict`, `headers`, and `headersHelper`. Write each item's `source` as an object type, because a relative path has no repository to resolve against (types: `settings`)
