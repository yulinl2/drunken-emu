---
id: env.claude-code-emit-session-state-events
kind: env
status: VERIFIED
title: "CLAUDE_CODE_EMIT_SESSION_STATE_EVENTS"
sources: [S81]
---

# CLAUDE_CODE_EMIT_SESSION_STATE_EVENTS

**Sources:** [S81](src.s81.md)

Set to `1` to add `session_state_changed` messages, which carry the session's state, to the message stream. Requires either the Agent SDK or `--print`, `--output-format stream-json`, and `--verbose`
