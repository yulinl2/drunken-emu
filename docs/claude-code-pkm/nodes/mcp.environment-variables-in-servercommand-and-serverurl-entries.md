---
id: mcp.environment-variables-in-servercommand-and-serverurl-entries
kind: mcp
status: VERIFIED
title: "Environment variables in serverCommand and serverUrl entries"
sources: [S63]
---

# Environment variables in serverCommand and serverUrl entries

**Sources:** [S63](src.s63.md)

`serverCommand` and `serverUrl` values expand before matching. Both the policy entry and the server's configured value go through `${VAR}` and `${VAR:-default}` expansion, so an entry written as `["${HOME}/bin/server"]` matches a server config that uses either the same reference or the expanded path. `serverName` values match literally and never expand.
