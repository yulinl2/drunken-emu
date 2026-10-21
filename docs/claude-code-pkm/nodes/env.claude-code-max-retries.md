---
id: env.claude-code-max-retries
kind: env
status: VERIFIED
title: "CLAUDE_CODE_MAX_RETRIES"
sources: [S81]
---

# CLAUDE_CODE_MAX_RETRIES

**Sources:** [S81](src.s81.md)

Override the number of times to retry failed API requests (default: 10). Retrying can stop earlier on `529` overloaded errors. For example, with an API key on an Opus model, it stops at the third `529` and shows Repeated 529 Overloaded errors. If you set a fallback model, Claude Code switches to that model rather than showing the error. Capped at 15 as of v2.1.186; as of v2.1.199, `CLAUDE_CODE_RETRY_WATCHDOG` raises the default and removes the cap. For unattended sessions that need to wait through longer outages, set `CLAUDE_CODE_RETRY_WATCHDOG` instead
