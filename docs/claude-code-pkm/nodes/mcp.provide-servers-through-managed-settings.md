---
id: mcp.provide-servers-through-managed-settings
kind: mcp
status: VERIFIED
title: "Provide servers through managed settings"
sources: [S63]
---

# Provide servers through managed settings

**Sources:** [S63](src.s63.md)

To give every user a set of remote MCP servers without taking exclusive control of MCP, list them under `managedMcpServers` in a managed settings source: server-managed settings, a Claude apps gateway policy, an MDM profile or registry policy, or `managed-settings.json`. Users keep the servers they add themselves and receive yours in addition. Requires Claude Code v2.1.259 or later. Earlier client
