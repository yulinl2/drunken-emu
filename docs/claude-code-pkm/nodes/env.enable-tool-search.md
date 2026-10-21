---
id: env.enable-tool-search
kind: env
status: VERIFIED
title: "ENABLE_TOOL_SEARCH"
sources: [S81]
---

# ENABLE_TOOL_SEARCH

**Sources:** [S81](src.s81.md)

Controls MCP tool search. Unset or `true` defers MCP tools, except in the cases that keep tool search off. `auto` turns tool search on once definitions reach 10% of the context window. `auto:N` sets a custom threshold, such as `auto:5` for 5%. `false` loads all tools upfront. If a gateway rejects tool search, see Tool search through an LLM gateway
