---
id: env.claude-auto-background-tasks
kind: env
status: VERIFIED
title: "CLAUDE_AUTO_BACKGROUND_TASKS"
sources: [S81]
---

# CLAUDE_AUTO_BACKGROUND_TASKS

**Sources:** [S81](src.s81.md)

Set to `1` to force-enable automatic backgrounding of long-running agent tasks. When enabled, a subagent moves to the background after running for approximately two minutes. If Claude queued a tool call such as a file edit behind the subagent, the subagent finishes in the foreground before that call starts. Also enables automatic backgrounding of long MCP tool calls in non-interactive mode on Claude Code v2.1.212 or later
