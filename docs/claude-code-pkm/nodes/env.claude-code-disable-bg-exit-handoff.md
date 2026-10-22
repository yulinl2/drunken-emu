---
id: env.claude-code-disable-bg-exit-handoff
kind: env
status: VERIFIED
title: "CLAUDE_CODE_DISABLE_BG_EXIT_HANDOFF"
sources: [S81]
---

# CLAUDE_CODE_DISABLE_BG_EXIT_HANDOFF

**Sources:** [S81](src.s81.md)

Set to `1` to stop a background session's in-flight work when the supervisor stops, restarts, or updates that session's process, instead of handing it to the session's next process. That work is the session's running background shell commands and dynamic workflows, plus background subagents as of v2.1.198. Affects only that handoff: backgrounding a session with `←` or `/background` still carries in-flight background work over. Requires Claude Code v2.1.196 or later
