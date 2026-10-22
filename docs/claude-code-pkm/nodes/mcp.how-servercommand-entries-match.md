---
id: mcp.how-servercommand-entries-match
kind: mcp
status: VERIFIED
title: "How serverCommand entries match"
sources: [S63]
---

# How serverCommand entries match

**Sources:** [S63](src.s63.md)

A `serverCommand` entry holds the command and its arguments as one array, as in `{ "serverCommand": ["npx", "-y", "server"] }`. Claude Code compares that array with the command and arguments in the server's configuration:
