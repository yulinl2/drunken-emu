---
id: env.claude-code-print-bg-wait-ceiling-ms
kind: env
status: VERIFIED
title: "CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS"
sources: [S81]
---

# CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS

**Sources:** [S81](src.s81.md)

Ceiling in milliseconds on idle waiting for background work, such as subagents and workflows, after the final turn in non-interactive mode with the `-p` flag. Idle waiting starts over each time Claude takes a turn to handle a background result. Default: `600000`, or 10 minutes. When idle waiting reaches the ceiling, Claude Code stops waiting for the remaining background tasks. A running background command that the main conversation started holds the run open past it. Set to `0` to wait indefinitely. Requires Claude Code v2.1.182 or later
