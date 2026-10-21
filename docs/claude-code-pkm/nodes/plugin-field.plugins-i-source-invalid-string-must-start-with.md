---
id: plugin-field.plugins-i-source-invalid-string-must-start-with
kind: plugin-field
status: VERIFIED
title: "plugins.i.source: Invalid string: must start with \"./\""
sources: [S51]
---

# plugins.i.source: Invalid string: must start with "./"

**Sources:** [S51](src.s51.md)

level: Error; field: A relative-path `source` without the leading `./`. Before v2.1.285, this mistake printed `Invalid input` instead
