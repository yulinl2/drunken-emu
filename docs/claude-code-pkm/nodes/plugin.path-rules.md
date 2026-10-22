---
id: plugin.path-rules
kind: plugin
status: VERIFIED
title: "Path rules"
sources: [S50]
---

# Path rules

**Sources:** [S50](src.s50.md)

Every component path in a manifest is relative to the plugin root and must start with `./`. A path such as `commands/foo.md` fails validation. `skills` and `mcpServers` each accept one form outside that rule:
