---
id: mcp.monitor-mcp-usage
kind: mcp
status: VERIFIED
title: "Monitor MCP usage"
sources: [S63]
---

# Monitor MCP usage

**Sources:** [S63](src.s63.md)

When you configure OpenTelemetry export, Claude Code can record which MCP servers and tools users invoke. Set `OTEL_LOG_TOOL_DETAILS=1` to include MCP server and tool names in tool events and on the cost and token counters, then aggregate them in your collector to see which servers your users actually connect to. See Monitoring to set up the exporter and for the full event schema.
