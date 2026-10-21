---
id: mcp.tool-search-through-an-llm-gateway
kind: mcp
status: VERIFIED
title: "Tool search through an LLM gateway"
sources: [S31]
---

# Tool search through an LLM gateway

**Sources:** [S31](src.s31.md)

When `ANTHROPIC_BASE_URL` points to a gateway, tool search is on by default, so requests include `defer_loading` tool fields and `tool_reference` blocks for the gateway to forward. While tool search is on, MCP tools are deferred. To load every tool upfront instead, set `ENABLE_TOOL_SEARCH=false` in your shell or your settings `env`. Before v2.1.304, tool search was off behind a gateway unless `ENA
