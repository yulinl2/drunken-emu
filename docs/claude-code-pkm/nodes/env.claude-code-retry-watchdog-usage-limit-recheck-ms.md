---
id: env.claude-code-retry-watchdog-usage-limit-recheck-ms
kind: env
status: VERIFIED
title: "CLAUDE_CODE_RETRY_WATCHDOG_USAGE_LIMIT_RECHECK_MS"
sources: [S81]
---

# CLAUDE_CODE_RETRY_WATCHDOG_USAGE_LIMIT_RECHECK_MS

**Sources:** [S81](src.s81.md)

Minimum interval in milliseconds between checks of whether a usage limit was already lifted, while a request waits for that limit to reset with `CLAUDE_CODE_RETRY_WATCHDOG` set. When a check finds the limit lifted, the request goes out at once. Give a whole number in plain digits from `60000`, one minute, to `10800000`, three hours. Checks are made only for a claude.ai subscription's session or weekly limit while usage credits aren't in use, and not while `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` is set. When this variable is unset or its value is outside that range, no checks are made. Requires Claude Code v2.1.305 or later
