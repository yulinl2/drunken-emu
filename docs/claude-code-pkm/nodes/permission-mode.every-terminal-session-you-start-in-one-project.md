---
id: permission-mode.every-terminal-session-you-start-in-one-project
kind: permission-mode
status: VERIFIED
title: "Every terminal session you start in one project"
sources: [S67]
---

# Every terminal session you start in one project

**Sources:** [S67](src.s67.md)

do this: Set `permissions.defaultMode` in the project's `.claude/settings.json`. Sessions you start in a terminal honor every value except `auto` and `bypassPermissions`; sessions the VS Code extension starts don't read project settings for the starting permission mode
