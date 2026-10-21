---
id: tool.windows-encoding-and-exit-codes
kind: tool
status: VERIFIED
title: "Windows encoding and exit codes"
sources: [S82]
---

# Windows encoding and exit codes

**Sources:** [S82](src.s82.md)

Redirection with `>` and `>>` writes UTF-8 files on PowerShell 5.1 Claude Code encodes text piped to a native command's standard input as UTF-8 Claude Code captures error output without ANSI escape sequences A command whose child process waits on standard input receives end-of-file instead of hanging
