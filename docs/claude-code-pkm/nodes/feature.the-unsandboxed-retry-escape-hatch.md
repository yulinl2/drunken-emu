---
id: feature.the-unsandboxed-retry-escape-hatch
kind: feature
status: VERIFIED
title: "The unsandboxed retry escape hatch"
sources: [S68]
---

# The unsandboxed retry escape hatch

**Sources:** [S68](src.s68.md)

The unsandboxed retry is an escape hatch for commands that fail inside the sandbox, such as tools that are incompatible with it. When the sandbox blocks a network connection, Claude Code names the denied host in the command's result, so Claude sees what was blocked. Claude analyzes the failure and may retry the command with the `dangerouslyDisableSandbox` parameter.
