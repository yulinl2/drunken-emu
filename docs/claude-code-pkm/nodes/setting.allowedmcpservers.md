---
id: setting.allowedmcpservers
kind: setting
status: VERIFIED
title: "allowedMcpServers"
sources: [S61]
---

# allowedMcpServers

**Sources:** [S61](src.s61.md)

Enforced as an empty allowlist until the value is fixed, so no MCP servers that users add are admitted. Servers your organization delivers through `managedMcpServers` still load, and `managed-mcp.json` servers load per Servers that skip the allowlist check. An individual invalid entry is stripped and the valid subset is enforced.
