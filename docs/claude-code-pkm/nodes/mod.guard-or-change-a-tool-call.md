---
id: mod.guard-or-change-a-tool-call
kind: mod
status: VERIFIED
title: "Guard or change a tool call"
sources: [S55]
---

# Guard or change a tool call

**Sources:** [S55](src.s55.md)

A `tool.call` hook sees each tool Claude is about to use, so it can refuse the call, change its arguments, or let it through. `tool.call` fires when Claude Code is about to run a tool, including calls a subagent makes and calls to MCP tools. `e.tool` is the tool's name and the tool's arguments are fields of `e`, such as `e.command` for Bash. When you call `next(e)`, Claude Code runs the permission
