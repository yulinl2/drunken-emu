---
id: mcp.local-scope
kind: mcp
status: VERIFIED
title: "Local scope"
sources: [S31]
---

# Local scope

**Sources:** [S31](src.s31.md)

Local scope is the default. A local-scoped server loads only in the project where you added it and stays private to you. Claude Code stores it in `~/.claude.json` under that project's path, so the same server won't appear in your other projects. Use local scope for personal development servers, experimental configurations, or servers with credentials you don't want in version control.
