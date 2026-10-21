---
id: hook-rule.stop-input
kind: hook-rule
status: VERIFIED
title: "Stop input"
sources: [S85]
---

# Stop input

**Sources:** [S85](src.s85.md)

In addition to the common input fields, Stop hooks receive `stop_hook_active`, `last_assistant_message`, `background_tasks`, and `session_crons`. The `stop_hook_active` field is `true` when Claude Code is already continuing as a result of a stop hook. Check this value or process the transcript to avoid blocking on a condition that will never resolve.
