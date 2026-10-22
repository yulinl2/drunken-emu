---
id: env.claude-code-bg-tasks-report-running
kind: env
status: VERIFIED
title: "CLAUDE_CODE_BG_TASKS_REPORT_RUNNING"
sources: [S81]
---

# CLAUDE_CODE_BG_TASKS_REPORT_RUNNING

**Sources:** [S81](src.s81.md)

Set to `0` to make a non-interactive session report an idle status to its host at every turn end, even while background work is still running. By default, the session keeps reporting a running status past turn end while background work such as a background agent or a workflow run is still live. This keeps a host that watches the status, such as a remote session list, from announcing that Claude is waiting for your input mid-work. Background shell commands, such as a dev server, don't hold the running status. The running-status default and the `0` opt-out require Claude Code v2.1.269 or later; on earlier versions, set `1` to hold the running status
