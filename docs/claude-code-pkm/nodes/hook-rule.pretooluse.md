---
id: hook-rule.pretooluse
kind: hook-rule
status: VERIFIED
title: "PreToolUse"
sources: [S85]
---

# PreToolUse

**Sources:** [S85](src.s85.md)

Runs after Claude creates tool parameters and before processing the tool call. Matches on any tool name except `EndConversation`: built-in tools such as `Bash`, `PowerShell`, `Edit`, `Write`, `Read`, `Glob`, `Grep`, `Agent`, `Workflow`, `WebFetch`, `WebSearch`, `AskUserQuestion`, and `ExitPlanMode`, and any MCP tool names.
