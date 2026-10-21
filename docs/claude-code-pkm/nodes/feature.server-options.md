---
id: feature.server-options
kind: feature
status: VERIFIED
title: "Server options"
sources: [S35]
---

# Server options

**Sources:** [S35](src.s35.md)

A channel sets these options in the `Server` constructor. The `instructions` and `capabilities.tools` fields are standard MCP; `capabilities.experimental['claude/channel']` and `capabilities.experimental['claude/channel/permission']` are the channel-specific additions:
