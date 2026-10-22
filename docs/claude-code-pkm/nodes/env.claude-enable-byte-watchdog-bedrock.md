---
id: env.claude-enable-byte-watchdog-bedrock
kind: env
status: VERIFIED
title: "CLAUDE_ENABLE_BYTE_WATCHDOG_BEDROCK"
sources: [S81]
---

# CLAUDE_ENABLE_BYTE_WATCHDOG_BEDROCK

**Sources:** [S81](src.s81.md)

Set to `1` to enable the byte-level streaming idle watchdog on Amazon Bedrock `vnd.amazon.eventstream` responses, which also enables the first-byte deadline on Bedrock streaming requests. Off by default. Configure the timeout with `CLAUDE_STREAM_IDLE_TIMEOUT_MS`
