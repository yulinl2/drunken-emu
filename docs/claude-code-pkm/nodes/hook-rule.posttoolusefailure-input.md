---
id: hook-rule.posttoolusefailure-input
kind: hook-rule
status: VERIFIED
title: "PostToolUseFailure input"
sources: [S85]
---

# PostToolUseFailure input

**Sources:** [S85](src.s85.md)

PostToolUseFailure hooks receive the same `tool_name` and `tool_input` fields as PostToolUse, along with error information as top-level fields. For an MCP tool, they also receive the `mcp_server` object. For example, a failed `npm test` command might deliver:
