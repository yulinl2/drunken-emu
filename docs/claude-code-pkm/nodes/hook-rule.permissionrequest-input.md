---
id: hook-rule.permissionrequest-input
kind: hook-rule
status: VERIFIED
title: "PermissionRequest input"
sources: [S85]
---

# PermissionRequest input

**Sources:** [S85](src.s85.md)

PermissionRequest hooks receive `tool_name` and `tool_input` fields like PreToolUse hooks, but without `tool_use_id`. For an MCP tool, they also receive the `mcp_server` object. An optional `permission_suggestions` array contains the permission updates Claude Code suggests for this request, such as adding an allow rule or changing the permission mode.
