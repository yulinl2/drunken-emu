---
id: feature.audit-mcp-activity
kind: feature
status: VERIFIED
title: "Audit MCP activity"
sources: [S65]
---

# Audit MCP activity

**Sources:** [S65](src.s65.md)

To capture MCP server activity with full call detail, enable the logs exporter and set `OTEL_LOG_TOOL_DETAILS=1`. Each MCP operation then produces structured events that carry the server name, tool name, and call arguments alongside the standard identity attributes:
