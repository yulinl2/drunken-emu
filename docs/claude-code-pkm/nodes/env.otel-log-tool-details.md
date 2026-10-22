---
id: env.otel-log-tool-details
kind: env
status: VERIFIED
title: "OTEL_LOG_TOOL_DETAILS"
sources: [S81]
---

# OTEL_LOG_TOOL_DETAILS

**Sources:** [S81](src.s81.md)

Set to `1` to include tool input arguments; MCP server names; user-authored workflow names; raw error strings on tool failures; the refusal `category` on `api_refusal` events; real agent, skill, plugin, and MCP server names on cost and token metrics; and other tool details in OpenTelemetry metrics, traces, and logs. Disabled by default to protect PII. Set it in your shell, user settings, or managed settings. Ignored in project and local settings, apart from the off values that section describes. See Monitoring
