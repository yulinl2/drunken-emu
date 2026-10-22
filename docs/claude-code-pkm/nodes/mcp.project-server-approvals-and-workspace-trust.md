---
id: mcp.project-server-approvals-and-workspace-trust
kind: mcp
status: VERIFIED
title: "Project server approvals and workspace trust"
sources: [S31]
---

# Project server approvals and workspace trust

**Sources:** [S31](src.s31.md)

`claude mcp list` and `claude mcp get` read `.mcp.json` approvals only from settings files that aren't checked into the repository until you trust the workspace by running `claude` in it and accepting the workspace trust dialog. A cloned repository can't approve its own servers: `enableAllProjectMcpServers` or `enabledMcpjsonServers` committed to the project's `.claude/settings.json` is ignored in
