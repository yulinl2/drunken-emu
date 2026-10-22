---
id: plugin.lsp-servers
kind: plugin
status: VERIFIED
title: "LSP servers"
sources: [S45]
---

# LSP servers

**Sources:** [S45](src.s45.md)

An LSP server gives Claude diagnostics and code navigation for a language. If an official code intelligence plugin already covers your language, install that instead of writing one. Otherwise declare the server in `.lsp.json` at the plugin root:
