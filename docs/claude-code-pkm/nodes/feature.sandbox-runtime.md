---
id: feature.sandbox-runtime
kind: feature
status: VERIFIED
title: "Sandbox runtime"
sources: [S69]
---

# Sandbox runtime

**Sources:** [S69](src.s69.md)

The `@anthropic-ai/sandbox-runtime` package wraps an entire process in the same Seatbelt or bubblewrap isolation that the built-in Bash sandbox uses. Running Claude Code through the runtime constrains the session's tools, hooks, and MCP servers as well as shell commands. The runtime is a beta research preview, and its configuration format may change as the package evolves.
