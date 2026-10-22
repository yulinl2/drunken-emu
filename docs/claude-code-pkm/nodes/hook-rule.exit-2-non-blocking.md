---
id: hook-rule.exit-2-non-blocking
kind: hook-rule
status: VERIFIED
title: "Exit code 2: non-blocking events"
sources: [S2]
---

# Exit code 2: non-blocking events

**Sources:** [S2](src.s2.md)

On other events exit 2 does not block. On PostToolUse and PostToolUseFailure, stderr goes to Claude. On SessionStart, SubagentStart, SessionEnd, CwdChanged, FileChanged, PostCompact and PostModelSwitch, stderr goes to the user. Other events ignore it, including PermissionRequest, PermissionDenied and StopFailure.
