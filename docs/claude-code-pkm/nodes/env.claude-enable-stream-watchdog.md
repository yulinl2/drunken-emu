---
id: env.claude-enable-stream-watchdog
kind: env
status: VERIFIED
title: "CLAUDE_ENABLE_STREAM_WATCHDOG"
sources: [S81]
---

# CLAUDE_ENABLE_STREAM_WATCHDOG

**Sources:** [S81](src.s81.md)

Set to `0` to force-disable the event-level streaming idle watchdog, or set to `1` to force-enable it. When unset, the watchdog is on by default for all providers. Before v2.1.196, the unset default was server-controlled on the direct Anthropic API and off on other providers. Configure the timeout with `CLAUDE_STREAM_IDLE_TIMEOUT_MS`; for the other stall timers that run alongside this one, see Streaming idle watchdogs
