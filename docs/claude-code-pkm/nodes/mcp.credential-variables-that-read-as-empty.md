---
id: mcp.credential-variables-that-read-as-empty
kind: mcp
status: VERIFIED
title: "Credential variables that read as empty"
sources: [S31]
---

# Credential variables that read as empty

**Sources:** [S31](src.s31.md)

In a remote server's `url` and `headers`, Claude Code reads credential variables from your environment as empty rather than expanding them. This keeps a project's `.mcp.json` or a plugin from sending your Claude Code or cloud provider credentials to a server it names. If you write `Bearer ${ANTHROPIC_AUTH_TOKEN}`, the server receives `Bearer ` with no credential and rejects the request, usually wi
