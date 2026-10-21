---
id: hook-rule.exit-code-2
kind: hook-rule
status: VERIFIED
title: "Exit code 2"
sources: [S85]
---

# Exit code 2

**Sources:** [S85](src.s85.md)

Exit with code 2 to block the action. On events that can block, Claude Code stops the action: a `PreToolUse` hook blocks the tool call, for example, and a `UserPromptSubmit` hook rejects the prompt.
