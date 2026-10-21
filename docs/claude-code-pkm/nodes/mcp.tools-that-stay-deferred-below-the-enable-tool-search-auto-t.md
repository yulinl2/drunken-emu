---
id: mcp.tools-that-stay-deferred-below-the-enable-tool-search-auto-t
kind: mcp
status: VERIFIED
title: "Tools that stay deferred below the ENABLE_TOOL_SEARCH=auto threshold"
sources: [S31]
---

# Tools that stay deferred below the ENABLE_TOOL_SEARCH=auto threshold

**Sources:** [S31](src.s31.md)

If `/context` labels tools `(deferred)` or `(loaded on-demand)` though their definitions total under the `auto` threshold, tool search was already on in this conversation and stayed on. The total can drop later, for example while MCP servers reconnect after you resume a session. You don't need to do anything: Claude loads each of those tools when a task needs it.
