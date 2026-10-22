---
id: feature.mcp-server-fails-to-start-from-some-directories
kind: feature
status: VERIFIED
title: "MCP server fails to start from some directories"
sources: [S40]
---

# MCP server fails to start from some directories

**Sources:** [S40](src.s40.md)

cause: `command` or `args` uses a relative file path; fix: Use absolute paths for local scripts. Executables on your `PATH` like `npx` or `uvx` work as-is.
