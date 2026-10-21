---
id: hook-rule.sessionstart
kind: hook-rule
status: VERIFIED
title: "SessionStart"
sources: [S85]
---

# SessionStart

**Sources:** [S85](src.s85.md)

Runs when Claude Code starts a new session or resumes an existing session. Useful for loading development context like existing issues or recent changes to your codebase, or setting up environment variables. For static context that doesn't require a script, use CLAUDE.md instead.
