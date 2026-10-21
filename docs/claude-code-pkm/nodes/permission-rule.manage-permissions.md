---
id: permission-rule.manage-permissions
kind: permission-rule
status: VERIFIED
title: "Manage permissions"
sources: [S66]
---

# Manage permissions

**Sources:** [S66](src.s66.md)

You can view and manage Claude Code's tool permissions with `/permissions`. The dialog lists all permission rules and the `settings.json` file each rule comes from. You can open the dialog while Claude is working: when you add or remove a rule, Claude Code applies the change starting with Claude's next tool call in the same turn. Before v2.1.234, Claude Code queued the command until the turn finis
