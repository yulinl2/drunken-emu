---
id: mcp.which-variables-a-helper-can-read
kind: mcp
status: VERIFIED
title: "Which variables a helper can read"
sources: [S31]
---

# Which variables a helper can read

**Sources:** [S31](src.s31.md)

A `headersHelper` that a repository or plugin supplies is a command you didn't write, so Claude Code runs it without the credential variables from your environment, such as `ANTHROPIC_API_KEY`. Where you configured the server decides whether this applies:
