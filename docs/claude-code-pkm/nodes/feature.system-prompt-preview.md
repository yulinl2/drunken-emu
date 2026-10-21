---
id: feature.system-prompt-preview
kind: feature
status: VERIFIED
title: "system_prompt_preview"
sources: [S65]
---

# system_prompt_preview

**Sources:** [S65](src.s65.md)

First 500 characters of the complete system prompt sent with the request (span: `claude_code.llm_request`; gated by: `OTEL_LOG_USER_PROMPTS`)
