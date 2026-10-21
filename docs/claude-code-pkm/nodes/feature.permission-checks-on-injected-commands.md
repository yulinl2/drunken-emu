---
id: feature.permission-checks-on-injected-commands
kind: feature
status: VERIFIED
title: "Permission checks on injected commands"
sources: [S32]
---

# Permission checks on injected commands

**Sources:** [S32](src.s32.md)

Injected commands never prompt for permission while the skill renders. Claude Code checks each one against your permission rules first. A command a deny rule matches aborts the invocation with `Shell command permission check failed for pattern "..."`.
