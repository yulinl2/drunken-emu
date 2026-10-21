---
id: feature.otel-log-raw-api-bodies
kind: feature
status: VERIFIED
title: "OTEL_LOG_RAW_API_BODIES"
sources: [S65]
---

# OTEL_LOG_RAW_API_BODIES

**Sources:** [S65](src.s65.md)

Emit the full Anthropic Messages API request and response JSON as `api_request_body` / `api_response_body` log events (default: disabled). Bodies include the entire conversation history. Enabling this implies consent to everything `OTEL_LOG_USER_PROMPTS`, `OTEL_LOG_TOOL_DETAILS`, and `OTEL_LOG_TOOL_CONTENT` would reveal (example values: `1` for inline bodies truncated at the content limit (60 KB by default), or `file:` for untruncated bodies on disk with a `body_ref` pointer in the event)
