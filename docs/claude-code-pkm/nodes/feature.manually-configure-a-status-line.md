---
id: feature.manually-configure-a-status-line
kind: feature
status: VERIFIED
title: "Manually configure a status line"
sources: [S78]
---

# Manually configure a status line

**Sources:** [S78](src.s78.md)

Add a `statusLine` field to your user settings (`~/.claude/settings.json`, where `~` is your home directory) or project settings. Set `type` to `"command"` and point `command` to a script path or an inline shell command. For a full walkthrough of creating a script, see Build a status line step by step.
