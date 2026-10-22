---
id: mcp.where-the-helper-runs
kind: mcp
status: VERIFIED
title: "Where the helper runs"
sources: [S31]
---

# Where the helper runs

**Sources:** [S31](src.s31.md)

Claude Code picks the `headersHelper` command's working directory from the configuration that declares the server. A `cd` that Claude runs in Bash doesn't move it, and `/cd` moves it only for servers that run from the session's primary working directory. Each row below gives the directory that a relative path in your `headersHelper` command resolves against.
