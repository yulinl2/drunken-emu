---
id: hook-rule.permissiondenied
kind: hook-rule
status: VERIFIED
title: "PermissionDenied"
sources: [S85]
---

# PermissionDenied

**Sources:** [S85](src.s85.md)

Runs when auto mode denies a tool call, including when it denies without a classifier verdict because a safety check separate from auto mode refused the classifier's own request or its response didn't parse. This hook only fires in auto mode: it doesn't run when you manually deny a permission dialog, when a `PreToolUse` hook blocks a call, or when a `deny` rule matches. Use it to log denials, adju
