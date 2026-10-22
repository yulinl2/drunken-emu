---
id: env.claude-code-child-session
kind: env
status: VERIFIED
title: "CLAUDE_CODE_CHILD_SESSION"
sources: [S81]
---

# CLAUDE_CODE_CHILD_SESSION

**Sources:** [S81](src.s81.md)

Set to `1` in subprocesses Claude Code spawns via the Bash, PowerShell, and Monitor tools, hook commands, and status line commands. Not set for stdio MCP server subprocesses, which are long-lived and outlive the session that spawned them. Unlike `CLAUDECODE`, this is only set by Claude Code itself when it launches a subprocess and not by IDE extensions, so it reliably distinguishes a nested session from a top-level `claude` launched in an IDE-integrated terminal. A nested interactive `claude` TUI started this way is automatically excluded from `--resume`, `--continue`, up-arrow history, and the `claude agents` list. Non-interactive `claude -p` sessions still persist. Set `CLAUDE_CODE_FORCE_SESSION_PERSISTENCE=1` to override this exclusion. Requires Claude Code v2.1.172 or later
