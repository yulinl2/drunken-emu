---
id: permission-rule.servers-in-mcp-json-including-ones-the-repository-approves-i
kind: permission-rule
status: VERIFIED
title: "Servers in .mcp.json, including ones the repository approves in its own settings"
sources: [S66]
---

# Servers in .mcp.json, including ones the repository approves in its own settings

**Sources:** [S66](src.s66.md)

Servers in `.mcp.json`, including ones the repository approves in its own settings (you trusted only a parent folder: Claude Code asks you before connecting them. The repository's own approvals don't count; `claude -p` or the sdk, folder never trusted: Connected without asking, approved or not. The SDK loads them only when `settingSources` includes project settings. `claude mcp list` in the same folder still reports such a server as pending)
