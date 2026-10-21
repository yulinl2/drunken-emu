---
id: env.claude-code-nonstreaming-timeout-retries
kind: env
status: VERIFIED
title: "CLAUDE_CODE_NONSTREAMING_TIMEOUT_RETRIES"
sources: [S81]
---

# CLAUDE_CODE_NONSTREAMING_TIMEOUT_RETRIES

**Sources:** [S81](src.s81.md)

Limit how many times Claude Code re-sends a non-streaming request that times out. With `0`, the request fails on the first timeout. See Tune retry behavior for the timeout. Requires Claude Code v2.1.285 or later
