---
id: env.claude-code-retry-watchdog-max-wait-ms
kind: env
status: VERIFIED
title: "CLAUDE_CODE_RETRY_WATCHDOG_MAX_WAIT_MS"
sources: [S81]
---

# CLAUDE_CODE_RETRY_WATCHDOG_MAX_WAIT_MS

**Sources:** [S81](src.s81.md)

Maximum time in milliseconds that each API request spends waiting out `429` and `529` errors when `CLAUDE_CODE_RETRY_WATCHDOG` is set. Once that time is spent, the next such error ends the request. Give a positive whole number in plain digits, such as `1800000` for 30 minutes. When unset, the wait has no limit. Requires Claude Code v2.1.295 or later
