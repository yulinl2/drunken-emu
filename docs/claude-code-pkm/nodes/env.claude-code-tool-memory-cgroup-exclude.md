---
id: env.claude-code-tool-memory-cgroup-exclude
kind: env
status: VERIFIED
title: "CLAUDE_CODE_TOOL_MEMORY_CGROUP_EXCLUDE"
sources: [S6]
---

# CLAUDE_CODE_TOOL_MEMORY_CGROUP_EXCLUDE

**Sources:** [S6](src.s6.md)

A list of process kinds exempt from the memory cap: mcp, lsp, hooks, plugin, helper and agent. none caps every kind; all-new caps only the Bash, PowerShell and Monitor commands (v2.1.246 or later).
