---
id: hook-rule.tools-that-require-user-interaction
kind: hook-rule
status: VERIFIED
title: "Tools that require user interaction"
sources: [S85]
---

# Tools that require user interaction

**Sources:** [S85](src.s85.md)

`AskUserQuestion` and `ExitPlanMode` require user interaction. In non-interactive mode with the `-p` flag, Claude Code offers them only when the run has a permission host to receive the prompt, such as an Agent SDK `canUseTool` callback.
