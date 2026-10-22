---
id: mcp.exempt-a-server-from-deferral
kind: mcp
status: VERIFIED
title: "Exempt a server from deferral"
sources: [S31]
---

# Exempt a server from deferral

**Sources:** [S31](src.s31.md)

If a server's tools should always be visible to Claude without a search step, set `alwaysLoad` to `true` in that server's configuration. The server's tools then load into context regardless of the `ENABLE_TOOL_SEARCH` setting. Use this for a small number of tools that Claude needs on every turn, since each upfront tool consumes context that would otherwise be available for your conversation.
