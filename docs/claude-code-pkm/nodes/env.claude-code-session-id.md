---
id: env.claude-code-session-id
kind: env
status: VERIFIED
title: "CLAUDE_CODE_SESSION_ID"
sources: [S81]
---

# CLAUDE_CODE_SESSION_ID

**Sources:** [S81](src.s81.md)

Set automatically to the current session ID in Bash and PowerShell tool subprocesses, hook command subprocesses, and stdio MCP server subprocesses. For Bash, PowerShell, and hooks this matches the `session_id` field in the hook JSON input and is updated on `/clear`. An MCP server subprocess retains the ID it was spawned with. On `--resume ` it receives the resumed ID, matching hooks and Bash. On `--continue` or `--resume` without an explicit ID it may receive the initial startup ID instead. Use to correlate scripts and external tools with the Claude Code session that launched them
