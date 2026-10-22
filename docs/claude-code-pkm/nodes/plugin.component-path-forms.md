---
id: plugin.component-path-forms
kind: plugin
status: VERIFIED
title: "Component path forms"
sources: [S50]
---

# Component path forms

**Sources:** [S50](src.s50.md)

Every component key accepts a path relative to the plugin root. `hooks`, `mcpServers`, `lspServers`, and `experimental.monitors` also accept inline configuration, `commands` also accepts an object map, and `mcpServers` also accepts MCP bundle paths and URLs. The examples that follow show each accepted shape once. For what each component does at runtime, see Plugin components.
