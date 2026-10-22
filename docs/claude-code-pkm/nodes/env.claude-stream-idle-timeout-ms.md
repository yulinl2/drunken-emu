---
id: env.claude-stream-idle-timeout-ms
kind: env
status: VERIFIED
title: "CLAUDE_STREAM_IDLE_TIMEOUT_MS"
sources: [S81]
---

# CLAUDE_STREAM_IDLE_TIMEOUT_MS

**Sources:** [S81](src.s81.md)

Timeout in milliseconds before the event- and byte-level streaming idle watchdogs close a stalled connection. When you set this variable explicitly, the minimum is `300000` (5 minutes); lower values are silently clamped to absorb extended thinking pauses and proxy buffering, and the byte-level watchdog caps the value at 30 minutes. `CLAUDE_BYTE_STREAM_IDLE_TIMEOUT_MS` takes precedence over this variable for the byte-level watchdog. For the per-watchdog unset defaults, see Streaming idle watchdogs
