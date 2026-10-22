---
id: setting.httphookallowedenvvars
kind: setting
status: VERIFIED
title: "httpHookAllowedEnvVars"
sources: [S61]
---

# httpHookAllowedEnvVars

**Sources:** [S61](src.s61.md)

Claude Code enforces an empty managed allowlist until you fix the value, so a header variable is interpolated only if another settings file names it. If only an individual entry is invalid, Claude Code strips that entry and enforces the rest.
