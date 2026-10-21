---
id: env.claude-code-stop-hook-block-cap
kind: env
status: VERIFIED
title: "CLAUDE_CODE_STOP_HOOK_BLOCK_CAP"
sources: [S81]
---

# CLAUDE_CODE_STOP_HOOK_BLOCK_CAP

**Sources:** [S81](src.s81.md)

Maximum number of consecutive times a Stop or SubagentStop hook may block the turn from ending before Claude Code overrides it and ends the turn anyway (default: 8). Set to `0` to disable the cap. Raise this if your hook legitimately needs more iterations to resolve
