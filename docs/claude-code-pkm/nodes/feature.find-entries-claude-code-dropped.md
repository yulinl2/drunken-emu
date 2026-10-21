---
id: feature.find-entries-claude-code-dropped
kind: feature
status: VERIFIED
title: "Find entries Claude Code dropped"
sources: [S61]
---

# Find entries Claude Code dropped

**Sources:** [S61](src.s61.md)

If your managed settings file, MDM profile, registry value, or server-managed payload fails schema validation, Claude Code first skips each individual entry it can repair, such as one invalid permission rule, and warns about each one. Claude Code then drops any value that still fails, unless the value belongs to one of the keys that fail closed instead.
