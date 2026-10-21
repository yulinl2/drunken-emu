---
id: mcp.automatic-backgrounding-of-long-tool-calls
kind: mcp
status: VERIFIED
title: "Automatic backgrounding of long tool calls"
sources: [S31]
---

# Automatic backgrounding of long tool calls

**Sources:** [S31](src.s31.md)

An MCP tool call in the main conversation that is still running after two minutes moves to a background task instead of blocking the session. Claude receives the task ID immediately and keeps working, and the result arrives as a task notification when the call settles.
