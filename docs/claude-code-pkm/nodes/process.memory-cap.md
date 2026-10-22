---
id: process.memory-cap
kind: process
status: VERIFIED
title: "Tool memory cap"
sources: [S6]
---

# Tool memory cap

**Sources:** [S6](src.s6.md)

On Linux and WSL, CLAUDE_CODE_TOOL_MEMORY_LIMIT caps the memory that Bash, PowerShell and Monitor commands share, using a memory cgroup. If the cgroup cannot be set up, commands run uncapped. Permission-gating hooks are excluded from the cap. See [CLAUDE_CODE_TOOL_MEMORY_LIMIT](env.claude-code-tool-memory-limit.md).
