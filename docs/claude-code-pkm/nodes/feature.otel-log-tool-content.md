---
id: feature.otel-log-tool-content
kind: feature
status: VERIFIED
title: "OTEL_LOG_TOOL_CONTENT"
sources: [S65]
---

# OTEL_LOG_TOOL_CONTENT

**Sources:** [S65](src.s65.md)

Enable logging of tool content in the `tool.output` span event (default: disabled). Span attributes carry tool content under their own gates. Requires tracing. Content is truncated at the content limit (60 KB by default) (example values: `1` to enable)
