---
id: env.claude-code-max-concurrent-subagents
kind: env
status: VERIFIED
title: "CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS"
sources: [S81]
---

# CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS

**Sources:** [S81](src.s81.md)

How many subagents can be running in one session before the Agent tool refuses to spawn another (default: 20). Accepts a positive whole number in plain digits; anything else is ignored, so the variable can adjust the cap but can't disable it. Requires Claude Code v2.1.217 or later
