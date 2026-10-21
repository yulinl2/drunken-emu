---
id: feature.permission-request-fields
kind: feature
status: VERIFIED
title: "Permission request fields"
sources: [S35]
---

# Permission request fields

**Sources:** [S35](src.s35.md)

The outbound notification from Claude Code is `notifications/claude/channel/permission_request`. Like the channel notification, the transport is standard MCP but the method and schema are Claude Code extensions. The `params` object has four string fields your server formats into the outgoing prompt:
