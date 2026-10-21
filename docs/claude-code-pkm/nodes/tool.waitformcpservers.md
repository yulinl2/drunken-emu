---
id: tool.waitformcpservers
kind: tool
status: VERIFIED
title: "WaitForMcpServers"
sources: [S82]
---

# WaitForMcpServers

**Sources:** [S82](src.s82.md)

Waits for one or more MCP servers that are still connecting in the background, so a request can use their tools without restarting the session. Claude calls it when a needed server isn't connected yet. Only appears when tool search is disabled, since `ToolSearch` handles the wait when it's enabled (permission required: No)
