---
id: mcp.how-a-server-is-evaluated
kind: mcp
status: VERIFIED
title: "How a server is evaluated"
sources: [S63]
---

# How a server is evaluated

**Sources:** [S63](src.s63.md)

Before loading a server, including one from `managed-mcp.json`, Claude Code runs the three checks below in order. It runs them again when a user reconnects a server or turns a disabled one back on in `/mcp`. In-process `type: "sdk"` servers, which the app that started the session registers, skip all three.
