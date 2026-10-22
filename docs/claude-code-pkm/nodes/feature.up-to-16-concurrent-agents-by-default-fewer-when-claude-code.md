---
id: feature.up-to-16-concurrent-agents-by-default-fewer-when-claude-code
kind: feature
status: VERIFIED
title: "Up to 16 concurrent agents by default, fewer when Claude Code has fewer CPUs available, including inside a CPU-limited container. To change the limit, set CLAUDE_CODE_WORKFLOW_MAX_CONCURRENT_AGENTS to a value from 1 to 256, which requires Claude Code v2.1.269 or later"
sources: [S29]
---

# Up to 16 concurrent agents by default, fewer when Claude Code has fewer CPUs available, including inside a CPU-limited container. To change the limit, set CLAUDE_CODE_WORKFLOW_MAX_CONCURRENT_AGENTS to a value from 1 to 256, which requires Claude Code v2.1.269 or later

**Sources:** [S29](src.s29.md)

why: Bounds local resource use
