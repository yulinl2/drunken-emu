---
id: plugin.enabled-in-project-settings-but-not-installed
kind: plugin
status: VERIFIED
title: "Enabled in project settings but not installed"
sources: [S49]
---

# Enabled in project settings but not installed

**Sources:** [S49](src.s49.md)

When a plugin's only `true` is in the project's `.claude/settings.json`, Claude Code doesn't fetch it onto a machine where it isn't installed, unless its marketplace entry has a relative-path source or a seed directory already holds it. Instead, the `/plugin` Errors tab shows `Plugin "" is enabled in project settings but isn't installed here`.
