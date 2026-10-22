---
id: env.claude-code-retry-watchdog
kind: env
status: VERIFIED
title: "CLAUDE_CODE_RETRY_WATCHDOG"
sources: [S81]
---

# CLAUDE_CODE_RETRY_WATCHDOG

**Sources:** [S81](src.s81.md)

Set to `1` for unattended sessions such as eval harnesses, CI jobs, or remote workers. Retries `429` and `529` capacity errors indefinitely instead of failing after `CLAUDE_CODE_MAX_RETRIES` attempts. Claude Code fails at once when a standard-speed request gets a `429` that reports a spend limit or exhausted usage credits, even one from a gateway spend cap that resets on a schedule. Before v2.1.239, the watchdog retried these indefinitely. For fast mode requests, see Handle rate limits. The watchdog backs off up to 5 minutes between attempts, or until the limit resets when the response carries a rate-limit reset time, so a session that hits a usage limit waits out the remaining window. On v2.1.199 or later it also raises the default retry count for other transient errors, such as server errors, timeouts, and dropped connections, to 300, roughly three hours of backoff, and removes the cap of 15 on `CLAUDE_CODE_MAX_RETRIES` if you set that variable explicitly. Requires Claude Code v2.1.186 or later
