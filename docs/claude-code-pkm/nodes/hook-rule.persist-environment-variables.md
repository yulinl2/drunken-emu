---
id: hook-rule.persist-environment-variables
kind: hook-rule
status: VERIFIED
title: "Persist environment variables"
sources: [S85]
---

# Persist environment variables

**Sources:** [S85](src.s85.md)

SessionStart hooks have access to the `CLAUDE_ENV_FILE` environment variable, which provides a file path where you can persist environment variables for the shell commands Claude runs later in the session.
