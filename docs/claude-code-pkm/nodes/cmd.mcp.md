---
id: cmd.mcp
kind: command
status: VERIFIED
title: "/mcp"
sources: [S80]
---

# /mcp

**Sources:** [S80](src.s80.md)

Manage MCP server connections and OAuth authentication. Run with no argument to open the interactive list, or pass `reconnect`, `enable`, or `disable` with a server name or `all` to change connection state without opening it. `reconnect all` retries every server that failed or needs authentication. In non-interactive mode (`-p`), running it with no argument prints a text summary of server status instead of opening the list
