---
id: mcp.allow-claude-in-chrome-alongside-the-managed-set
kind: mcp
status: VERIFIED
title: "Allow Claude in Chrome alongside the managed set"
sources: [S63]
---

# Allow Claude in Chrome alongside the managed set

**Sources:** [S63](src.s63.md)

By default, when you deploy `managed-mcp.json`, Claude Code blocks the built-in Claude in Chrome server in terminal sessions. Users don't get the extension install prompt, and a session where the user turned on Chrome by default starts without it and prints no warning. If a user who could otherwise run Claude in Chrome starts `claude --chrome`, Claude Code exits at startup with an error that names
