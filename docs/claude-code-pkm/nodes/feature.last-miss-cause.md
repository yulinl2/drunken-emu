---
id: feature.last-miss-cause
kind: feature
status: VERIFIED
title: "Last miss cause"
sources: [S78]
---

# Last miss cause

**Sources:** [S78](src.s78.md)

The `last_miss_cause` object reports what Claude Code identified as the likely cause of the most recent miss. Its `causes` array holds one or more cause names, such as `tools_changed`, `system_prompt_changed`, `ttl_expired_5m`, or `likely_server_side`. The object is `null` until the session's first miss, and again whenever Claude Code couldn't identify a cause for the most recent miss. Requires Cl
