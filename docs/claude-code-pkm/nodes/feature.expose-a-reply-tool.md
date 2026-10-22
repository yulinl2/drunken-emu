---
id: feature.expose-a-reply-tool
kind: feature
status: VERIFIED
title: "Expose a reply tool"
sources: [S35]
---

# Expose a reply tool

**Sources:** [S35](src.s35.md)

If your channel is two-way, like a chat bridge rather than an alert forwarder, expose a standard MCP tool that Claude can call to send messages back. Nothing about the tool registration is channel-specific. A reply tool has three components:
