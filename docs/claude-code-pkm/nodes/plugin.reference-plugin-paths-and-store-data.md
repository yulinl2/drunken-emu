---
id: plugin.reference-plugin-paths-and-store-data
kind: plugin
status: VERIFIED
title: "Reference plugin paths and store data"
sources: [S45]
---

# Reference plugin paths and store data

**Sources:** [S45](src.s45.md)

You don't know where your plugin will be installed, so refer to its files and data through these variables rather than fixed paths. They're substituted in skill, command, and agent content, in hook and monitor commands, and in MCP and LSP server configurations. They're also exported to hook, MCP, and LSP processes:
