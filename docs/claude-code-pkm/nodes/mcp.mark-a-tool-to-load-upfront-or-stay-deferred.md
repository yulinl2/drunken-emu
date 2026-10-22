---
id: mcp.mark-a-tool-to-load-upfront-or-stay-deferred
kind: mcp
status: VERIFIED
title: "Mark a tool to load upfront or stay deferred"
sources: [S31]
---

# Mark a tool to load upfront or stay deferred

**Sources:** [S31](src.s31.md)

To control how one of your server's tools loads, set `"anthropic/alwaysLoad"` in that tool's `_meta` object. The person who adds your server to Claude Code can also set `alwaysLoad` for the whole server in their configuration, and their setting can override yours:
