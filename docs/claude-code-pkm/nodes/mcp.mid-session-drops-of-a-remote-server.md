---
id: mcp.mid-session-drops-of-a-remote-server
kind: mcp
status: VERIFIED
title: "Mid-session drops of a remote server"
sources: [S31]
---

# Mid-session drops of a remote server

**Sources:** [S31](src.s31.md)

Claude Code first tries to reconnect a dropped remote server up to five times with exponential backoff, starting at a one-second delay and doubling it each time:
