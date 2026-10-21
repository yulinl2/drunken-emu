---
id: env.otel-log-assistant-responses
kind: env
status: VERIFIED
title: "OTEL_LOG_ASSISTANT_RESPONSES"
sources: [S81]
---

# OTEL_LOG_ASSISTANT_RESPONSES

**Sources:** [S81](src.s81.md)

Set to `1` to include the model's response text on `assistant_response` OpenTelemetry log events. When unset, Claude Code uses the value of `OTEL_LOG_USER_PROMPTS` instead. Set to `0` to keep responses redacted even when `OTEL_LOG_USER_PROMPTS` is set. Set it in your shell, user settings, or managed settings. Ignored in project and local settings. Requires Claude Code v2.1.193 or later. See Monitoring
