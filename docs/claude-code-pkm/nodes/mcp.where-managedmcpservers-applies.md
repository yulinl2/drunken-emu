---
id: mcp.where-managedmcpservers-applies
kind: mcp
status: VERIFIED
title: "Where managedMcpServers applies"
sources: [S63]
---

# Where managedMcpServers applies

**Sources:** [S63](src.s63.md)

Claude Code reads `managedMcpServers` from the managed source it selects under How Claude Code combines managed sources. When that source sets `managedSourcesBehavior` to `"merge"`, Claude Code provides the servers from every admin source instead, and when two sources define the same name, the higher-ranked source's entry applies whole. It never reads the key from the user-writable HKCU registry,
