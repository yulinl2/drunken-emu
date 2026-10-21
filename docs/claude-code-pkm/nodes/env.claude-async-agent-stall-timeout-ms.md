---
id: env.claude-async-agent-stall-timeout-ms
kind: env
status: VERIFIED
title: "CLAUDE_ASYNC_AGENT_STALL_TIMEOUT_MS"
sources: [S81]
---

# CLAUDE_ASYNC_AGENT_STALL_TIMEOUT_MS

**Sources:** [S81](src.s81.md)

Stall timeout in milliseconds for subagents. Also covers workflow agents on Claude Code v2.1.286 or later. Default `600000` (10 minutes); if you raise `CLAUDE_STREAM_IDLE_TIMEOUT_MS` while the stream watchdog is on, the default rises with it, as Handle slow or stalled API responses describes
