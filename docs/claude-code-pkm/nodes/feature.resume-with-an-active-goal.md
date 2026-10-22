---
id: feature.resume-with-an-active-goal
kind: feature
status: VERIFIED
title: "Resume with an active goal"
sources: [S37]
---

# Resume with an active goal

**Sources:** [S37](src.s37.md)

When you resume a session, Claude Code restores a goal that was still active when the session ended. Claude Code restores it on every resume route: `--continue`, `--resume` with a session ID, name, or transcript file path, and the session picker. Before v2.1.239, Claude Code restored the goal on every route except the `claude --resume` picker.
