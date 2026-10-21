---
id: permission-rule.project-allow-rules-and-workspace-trust
kind: permission-rule
status: VERIFIED
title: "Project allow rules and workspace trust"
sources: [S66]
---

# Project allow rules and workspace trust

**Sources:** [S66](src.s66.md)

`permissions.allow` rules and `permissions.additionalDirectories` entries in a project's `.claude/settings.json` grant capability, so Claude Code applies them only after you accept the workspace trust dialog for that folder. The dialog lists the rules and directories the folder would grant so you can review them first. `deny` and `ask` rules aren't affected, since they only restrict.
