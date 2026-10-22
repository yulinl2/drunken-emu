---
id: env.claude-byte-stream-idle-timeout-ms
kind: env
status: VERIFIED
title: "CLAUDE_BYTE_STREAM_IDLE_TIMEOUT_MS"
sources: [S81]
---

# CLAUDE_BYTE_STREAM_IDLE_TIMEOUT_MS

**Sources:** [S81](src.s81.md)

Timeout in milliseconds for the byte-level streaming idle watchdog; when set, it takes precedence over `CLAUDE_STREAM_IDLE_TIMEOUT_MS` for that watchdog and leaves the event-level watchdog unchanged. Claude Code clamps this variable to between 10 seconds and 30 minutes. Requires Claude Code v2.1.210 or later
