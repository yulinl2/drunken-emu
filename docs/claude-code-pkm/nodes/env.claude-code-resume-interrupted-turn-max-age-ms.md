---
id: env.claude-code-resume-interrupted-turn-max-age-ms
kind: env
status: VERIFIED
title: "CLAUDE_CODE_RESUME_INTERRUPTED_TURN_MAX_AGE_MS"
sources: [S81]
---

# CLAUDE_CODE_RESUME_INTERRUPTED_TURN_MAX_AGE_MS

**Sources:** [S81](src.s81.md)

Maximum age in milliseconds of the last transcript message for a session that ended mid-turn to continue automatically on resume. When the last message is older than this bound, Claude Code skips the `CLAUDE_CODE_RESUME_INTERRUPTED_TURN` automatic resume and its `CLAUDE_CODE_RESUME_PROMPT` continuation message, and the session starts idle so you continue explicitly. Unset or `0` sets no bound, except that some turns resume only within six hours of their last message, such as one that ended with an API error. A positive value bounds every turn, including those; a negative or non-numeric value applies a one-hour bound. Spawn scripts for long-running agents can set this so a restart against an old transcript doesn't re-run a stale prompt. Claude Code sets a one-hour bound itself when it restarts a crashed agent view session that inherited its conversation from an interactive session. Requires Claude Code v2.1.211 or later
