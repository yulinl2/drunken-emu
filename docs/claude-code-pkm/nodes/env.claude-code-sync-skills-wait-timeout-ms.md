---
id: env.claude-code-sync-skills-wait-timeout-ms
kind: env
status: VERIFIED
title: "CLAUDE_CODE_SYNC_SKILLS_WAIT_TIMEOUT_MS"
sources: [S81]
---

# CLAUDE_CODE_SYNC_SKILLS_WAIT_TIMEOUT_MS

**Sources:** [S81](src.s81.md)

Timeout in milliseconds for the first query to wait for the initial skill list when `CLAUDE_CODE_SYNC_SKILLS` is set (default: 5000). When exceeded, the first query runs with whichever skills have arrived. The downloads finish in the background either way, and Claude waits for a skill's download when it invokes that skill
