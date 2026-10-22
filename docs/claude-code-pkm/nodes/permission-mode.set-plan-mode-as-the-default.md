---
id: permission-mode.set-plan-mode-as-the-default
kind: permission-mode
status: VERIFIED
title: "Set plan mode as the default"
sources: [S67]
---

# Set plan mode as the default

**Sources:** [S67](src.s67.md)

To make plan mode the default for a project's terminal sessions, set `defaultMode` to `plan` in `.claude/settings.json`, placed as the example under Start in a different permission mode shows. Conversations the VS Code extension starts don't read project settings for the starting permission mode. There, set `claudeCode.initialPermissionMode` to `plan` in your VS Code user settings instead.
