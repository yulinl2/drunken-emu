---
id: env.claude-code-overloaded-retry-base-delay-ms
kind: env
status: VERIFIED
title: "CLAUDE_CODE_OVERLOADED_RETRY_BASE_DELAY_MS"
sources: [S81]
---

# CLAUDE_CODE_OVERLOADED_RETRY_BASE_DELAY_MS

**Sources:** [S81](src.s81.md)

Starting delay in milliseconds, in place of the default 500, of the exponential backoff between automatic retries of a request that the API rejects with a `529` overloaded error. Raise it to spread the retries over a longer window when the API is at capacity. Give whole milliseconds from 500 to 32000 in plain digits; Claude Code treats any other value as unset. Has no effect when `CLAUDE_CODE_RETRY_WATCHDOG` is set to `1`, or when the rejected request was sent in fast mode. Requires Claude Code v2.1.292 or later
