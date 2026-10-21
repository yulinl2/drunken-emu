---
id: env.api-force-idle-timeout
kind: env
status: VERIFIED
title: "API_FORCE_IDLE_TIMEOUT"
sources: [S81]
---

# API_FORCE_IDLE_TIMEOUT

**Sources:** [S81](src.s81.md)

Override the 5-minute body idle timeout that aborts a streaming model response when no bytes arrive. Set to `0` to turn the timeout off, for example when a slow gateway or local model pauses longer than 5 minutes between chunks, or `1` to keep it on for every provider. When unset, the timeout is active on providers other than the direct Anthropic API, Claude Platform on AWS, and Amazon Bedrock with `CLAUDE_ENABLE_BYTE_WATCHDOG_BEDROCK=1` set. The stream watchdogs run independently of it and abort a long silent pause even when you set `0` here
