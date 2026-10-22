---
id: hook-rule.permissiondenied-input
kind: hook-rule
status: VERIFIED
title: "PermissionDenied input"
sources: [S85]
---

# PermissionDenied input

**Sources:** [S85](src.s85.md)

In addition to the common input fields, PermissionDenied hooks receive `tool_name`, `tool_input`, `tool_use_id`, and `reason`. For an MCP tool, they also receive the `mcp_server` object.
