---
id: mcp.organization-controls-on-connector-tools
kind: mcp
status: VERIFIED
title: "Organization controls on connector tools"
sources: [S31]
---

# Organization controls on connector tools

**Sources:** [S31](src.s31.md)

Your organization can set per-tool controls on claude.ai connectors. Claude Code reads these settings at startup and enforces them locally, except in the desktop app's local and SSH sessions. There, the desktop app withholds `blocked` tools before it delivers a connector, and the `ask` setting doesn't reach Claude Code, so it applies the session's ordinary permission rules to those tools instead o
