---
id: env.claude-code-sessionend-hooks-timeout-ms
kind: env
status: VERIFIED
title: "CLAUDE_CODE_SESSIONEND_HOOKS_TIMEOUT_MS"
sources: [S81]
---

# CLAUDE_CODE_SESSIONEND_HOOKS_TIMEOUT_MS

**Sources:** [S81](src.s81.md)

Override the time budget in milliseconds for SessionEnd hooks. The value is also the timeout for each hook that sets no `timeout` of its own. Applies to session exit, `/clear`, and switching sessions via interactive `/resume`. By default the budget is 1.5 seconds, automatically raised to the highest per-hook `timeout` configured in settings files, up to 60 seconds. Timeouts on plugin-provided hooks do not raise the budget
