---
id: env.claude-code-goal-checkin-minutes
kind: env
status: VERIFIED
title: "CLAUDE_CODE_GOAL_CHECKIN_MINUTES"
sources: [S81]
---

# CLAUDE_CODE_GOAL_CHECKIN_MINUTES

**Sources:** [S81](src.s81.md)

How many minutes background work can keep an active goal waiting before Claude Code asks Claude to check on it. Default `30`. Set `0` to turn check-ins off. Give whole minutes in plain digits, at most `10080`, which is one week. Claude Code treats any other value as unset and uses the default. Requires Claude Code v2.1.234 or later
