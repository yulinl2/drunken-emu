---
id: env.claude-code-auto-mode-server
kind: env
status: VERIFIED
title: "CLAUDE_CODE_AUTO_MODE_SERVER"
sources: [S81]
---

# CLAUDE_CODE_AUTO_MODE_SERVER

**Sources:** [S81](src.s81.md)

Controls whether Claude Code asks the server to review auto mode actions. Set to `0` to use Claude Code's own classifier requests instead. On a direct connection to the Anthropic API, requires v2.1.281 or later. The linked section lists which sessions ask the server when the variable is unset, and from which version. Requires Claude Code v2.1.271 or later
