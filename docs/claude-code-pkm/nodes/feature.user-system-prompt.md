---
id: feature.user-system-prompt
kind: feature
status: VERIFIED
title: "user_system_prompt"
sources: [S65]
---

# user_system_prompt

**Sources:** [S65](src.s65.md)

Only the system prompt text you provide via the `systemPrompt` SDK option or `--system-prompt` and `--append-system-prompt` flags. Emitted once per session rather than per request (span: `claude_code.llm_request`; gated by: `OTEL_LOG_USER_PROMPTS`)
