---
id: tool.websocket-source
kind: tool
status: VERIFIED
title: "WebSocket source"
sources: [S82]
---

# WebSocket source

**Sources:** [S82](src.s82.md)

When a server already pushes events over a WebSocket, Claude can connect to it directly instead of writing a polling script. Each kind of socket activity either becomes an event or ends the watch:
