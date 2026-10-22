---
id: feature.otel-log-assistant-responses
kind: feature
status: VERIFIED
title: "OTEL_LOG_ASSISTANT_RESPONSES"
sources: [S65]
---

# OTEL_LOG_ASSISTANT_RESPONSES

**Sources:** [S65](src.s65.md)

Enable logging of assistant response text on `assistant_response` events (default: disabled). When unset, falls back to the value of `OTEL_LOG_USER_PROMPTS` (example values: `1` to enable, `0` to keep redacted)
