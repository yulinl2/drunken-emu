---
id: mcp.notification-streams-on-the-v2-runtime
kind: mcp
status: VERIFIED
title: "Notification streams on the v2 runtime"
sources: [S31]
---

# Notification streams on the v2 runtime

**Sources:** [S31](src.s31.md)

On the v2 runtime, Claude Code receives `list_changed` notifications from a server on the newer protocol revision over a stream it holds open. When the stream closes, Claude Code reopens it, with two limits:
