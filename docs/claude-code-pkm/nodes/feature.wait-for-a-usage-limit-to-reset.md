---
id: feature.wait-for-a-usage-limit-to-reset
kind: feature
status: VERIFIED
title: "Wait for a usage limit to reset"
sources: [S83]
---

# Wait for a usage limit to reset

**Sources:** [S83](src.s83.md)

When a claude.ai usage limit stops Claude mid-task, Claude Code waits in the open session and continues the task on its own after the limit resets. Automatic continue is on by default in interactive sessions signed in with a claude.ai subscription. Requires Claude Code v2.1.234 or later.
