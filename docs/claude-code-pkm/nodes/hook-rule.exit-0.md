---
id: hook-rule.exit-0
kind: hook-rule
status: VERIFIED
title: "Exit code 0"
sources: [S2]
---

# Exit code 0

**Sources:** [S2](src.s2.md)

Success. A single JSON object on stdout is parsed. Plain stdout is added to Claude's context only on UserPromptSubmit, UserPromptExpansion, SessionStart and PostModelSwitch. Stderr from an exit-0 hook never reaches Claude.
