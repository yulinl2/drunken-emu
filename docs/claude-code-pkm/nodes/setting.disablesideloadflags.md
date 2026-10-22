---
id: setting.disablesideloadflags
kind: setting
status: VERIFIED
title: "disableSideloadFlags"
sources: [S61]
---

# disableSideloadFlags

**Sources:** [S61](src.s61.md)

Reject the `--plugin-dir`, `--plugin-url`, `--agents`, and `--mcp-config` flags at startup. In cloud sessions, Claude Code instead starts the session and drops the server-delivered `--mcp-config` servers, apart from the exceptions its reference entry lists. Requires Claude Code v2.1.193 or later
