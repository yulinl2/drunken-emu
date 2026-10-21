---
id: feature.otel-log-tool-details
kind: feature
status: VERIFIED
title: "OTEL_LOG_TOOL_DETAILS"
sources: [S65]
---

# OTEL_LOG_TOOL_DETAILS

**Sources:** [S65](src.s65.md)

Enable logging of tool parameters and input arguments in tool events and trace span attributes: Bash commands, MCP server and tool names, skill names, user-authored workflow names, and tool input. Also enables custom, plugin, and MCP command names on `user_prompt` events, and real agent, skill, plugin, and MCP server and tool names on the cost and token counters (default: disabled). For Claude Desktop's built-in servers, in sessions Claude Desktop owns, `mcp_server_name`/`mcp_tool_name` emit on `tool_decision`/`tool_result` even with the flag off. The exception requires Claude Code v2.1.214 or later (example values: `1` to enable)
