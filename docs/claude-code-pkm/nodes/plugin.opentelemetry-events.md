---
id: plugin.opentelemetry-events
kind: plugin
status: VERIFIED
title: "OpenTelemetry events"
sources: [S59]
---

# OpenTelemetry events

**Sources:** [S59](src.s59.md)

`claude_code.plugin_installed` records each install, and `claude_code.plugin_loaded` records each enabled plugin at session start. Both events redact or omit third-party plugin and marketplace names unless you set `OTEL_LOG_TOOL_DETAILS=1`, as Redacted plugin names in your backend shows. Field lists are under Plugin installed event and Plugin loaded event.
