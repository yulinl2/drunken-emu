---
id: env.otel-log-raw-api-bodies
kind: env
status: VERIFIED
title: "OTEL_LOG_RAW_API_BODIES"
sources: [S81]
---

# OTEL_LOG_RAW_API_BODIES

**Sources:** [S81](src.s81.md)

Emit Anthropic Messages API request and response JSON as `api_request_body` / `api_response_body` log events. Set to `1` for inline bodies truncated at the content limit, or `file:` to write untruncated bodies to disk and emit a `body_ref` path instead. `CLAUDE_CODE_OTEL_CONTENT_MAX_LENGTH` configures the content limit, 60 KB by default. Disabled by default; bodies include the entire conversation history. Set it in your shell, user settings, or managed settings. Ignored in project and local settings. See Monitoring
