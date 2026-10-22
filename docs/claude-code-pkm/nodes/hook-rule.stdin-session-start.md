---
id: hook-rule.stdin-session-start
kind: hook-rule
status: VERIFIED
title: "Stdin: SessionStart fields"
sources: [S2]
---

# Stdin: SessionStart fields

**Sources:** [S2](src.s2.md)

SessionStart adds source (startup, resume, clear, compact or fork), model (may be absent), agent_type (with --agent) and session_title (when set). On resume or fork after a prior response, it also adds seconds_since_last_response, context_tokens, prompt_cache_likely_expired and estimated_cache_write_usd.

## Linked from

- [SessionStart](hook.session-start.md)
