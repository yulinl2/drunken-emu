---
id: hook-field.permissiondenied
kind: hook-field
status: VERIFIED
title: "PermissionDenied"
sources: [S85]
---

# PermissionDenied

**Sources:** [S85](src.s85.md)

Exit code and stderr are ignored because the denial already occurred. Use JSON `hookSpecificOutput.retry: true` to tell the model it may retry; Claude Code ignores `retry: true` for no-verdict denials (can block?: No)
