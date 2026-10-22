---
id: env.claude-code-overloaded-retry-max-delay-ms
kind: env
status: VERIFIED
title: "CLAUDE_CODE_OVERLOADED_RETRY_MAX_DELAY_MS"
sources: [S81]
---

# CLAUDE_CODE_OVERLOADED_RETRY_MAX_DELAY_MS

**Sources:** [S81](src.s81.md)

Ceiling in milliseconds, in place of the default 32000, on the exponential backoff between automatic retries of a request that the API rejects with a `529` overloaded error. Raise it so that later retries keep spreading apart when the API is at capacity. Give whole milliseconds from 32000 to 64000 in plain digits; Claude Code treats any other value as unset. Has no effect when `CLAUDE_CODE_RETRY_WATCHDOG` is set to `1`, or when the rejected request was sent in fast mode. Requires Claude Code v2.1.296 or later
