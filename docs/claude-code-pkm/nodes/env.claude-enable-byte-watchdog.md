---
id: env.claude-enable-byte-watchdog
kind: env
status: VERIFIED
title: "CLAUDE_ENABLE_BYTE_WATCHDOG"
sources: [S81]
---

# CLAUDE_ENABLE_BYTE_WATCHDOG

**Sources:** [S81](src.s81.md)

Set to `1` to force-enable the byte-level streaming idle watchdog, or set to `0` to force-disable it. `0` also turns off the first-byte deadline on the connections where that deadline runs. When unset, the watchdog is enabled by default for direct Anthropic API and Claude Platform on AWS connections, and for streaming responses on gateway connections reached through `ANTHROPIC_BASE_URL` or `ANTHROPIC_AWS_BASE_URL`; before v2.1.222 it didn't run on those gateway connections, so the event-level watchdog could report a stall there even while keep-alive pings were arriving. For timeouts and how the timers interact, see Streaming idle watchdogs
