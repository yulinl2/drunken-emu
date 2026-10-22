---
id: hook.session-start
kind: hook
status: VERIFIED
title: "SessionStart"
sources: [S2]
---

# SessionStart

**Sources:** [S2](src.s2.md)

Fires when a session begins or resumes. Matchers: startup, resume, clear, compact, fork. Plain stdout is added to context. Handler types: command and mcp_tool only. Exit 2 shows stderr to the user only. Input: [Stdin: SessionStart fields](hook-rule.stdin-session-start.md).

## Linked from

- [Observation: repo registers a SessionStart hook](obs.repo-session-start-hook.md)
- [Observation: SessionStart banner not visible](obs.session-start-banner-not-visible.md)
- [Q1: Does a hook added mid-session take effect?](question.q1.md)
- [session-start-hook](skill.session-start-hook.md)
