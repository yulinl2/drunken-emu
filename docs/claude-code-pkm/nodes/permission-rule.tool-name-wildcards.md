---
id: permission-rule.tool-name-wildcards
kind: permission-rule
status: VERIFIED
title: "Tool name wildcards"
sources: [S66]
---

# Tool name wildcards

**Sources:** [S66](src.s66.md)

Deny and ask rules also accept glob patterns in the tool-name position. The pattern must match the full tool name: `"*"` matches every tool, and `"mcp*"` matches every MCP tool across all servers. A tool matched by a bare-name glob deny rule is removed from Claude's context, the same as a bare tool name, including the `EndConversation` exception: a glob deny can't remove it while any other tool re
