---
id: hook-rule.permissionrequest
kind: hook-rule
status: VERIFIED
title: "PermissionRequest"
sources: [S85]
---

# PermissionRequest

**Sources:** [S85](src.s85.md)

Runs when Claude Code is about to ask you for permission to use a tool. In sessions that can't show a prompt, such as background subagents in non-interactive mode, Claude Code still runs these hooks, and if no hook returns a decision, it denies the tool call. For a call that reaches a `--permission-prompt-tool` or the Agent SDK's `canUseTool` callback, the hooks run alongside your host, and whiche
