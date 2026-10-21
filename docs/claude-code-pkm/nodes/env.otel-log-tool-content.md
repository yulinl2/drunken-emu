---
id: env.otel-log-tool-content
kind: env
status: VERIFIED
title: "OTEL_LOG_TOOL_CONTENT"
sources: [S81]
---

# OTEL_LOG_TOOL_CONTENT

**Sources:** [S81](src.s81.md)

Set to `1` to include tool content in the `tool.output` OpenTelemetry span event. Span attributes carry tool content under their own gates. Requires tracing. Disabled by default to protect sensitive data. Set it in your shell, user settings, or managed settings. Ignored in project and local settings, apart from the off values that section describes. See Monitoring
