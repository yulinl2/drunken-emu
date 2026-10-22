---
id: feature.run-your-checks-before-each-commit
kind: feature
status: VERIFIED
title: "Run your checks before each commit"
sources: [S32]
---

# Run your checks before each commit

**Sources:** [S32](src.s32.md)

When a session starts with a skill named `verify` or `simplify` in place, Claude Code's commit instructions tell Claude to run it right before each commit, except for changes to docs or tests. This requires Claude Code v2.1.286 or later. Claude gets that instruction when these conditions hold at the start of the session:
