---
id: mcp.trust-a-folder-before-its-headershelper-runs
kind: mcp
status: VERIFIED
title: "Trust a folder before its headersHelper runs"
sources: [S31]
---

# Trust a folder before its headersHelper runs

**Sources:** [S31](src.s31.md)

Claude Code executes a `headersHelper` as an arbitrary shell command. For a server in a project `.mcp.json` or at local scope, it runs the helper only after you accept the trust dialog for the project directory the server is declared in. Before v2.1.238, a `claude -p` or SDK session ran these helpers without checking trust, and an interactive session ran them once you had trusted a parent folder.
