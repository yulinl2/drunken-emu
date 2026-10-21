---
id: hook-rule.taskcreated-decision-control
kind: hook-rule
status: VERIFIED
title: "TaskCreated decision control"
sources: [S85]
---

# TaskCreated decision control

**Sources:** [S85](src.s85.md)

A TaskCreated hook can block the creation with exit code 2 or with a JSON decision. Either way, Claude Code deletes the task and returns your message to Claude as the tool's error. Claude Code ignores `continue: false` from this event and Claude keeps working.
