---
id: mcp.how-claude-code-stops-a-stdio-server
kind: mcp
status: VERIFIED
title: "How Claude Code stops a stdio server"
sources: [S31]
---

# How Claude Code stops a stdio server

**Sources:** [S31](src.s31.md)

When Claude Code disconnects a stdio server, for example when your session ends, it signals the server process and waits briefly for it to exit before forcing it to stop. If your server saves state or removes lock files at shutdown, handle the signal for your platform and finish within that time:
