---
id: feature.workspace-trust-required
kind: feature
status: VERIFIED
title: "Workspace trust required"
sources: [S78]
---

# Workspace trust required

**Sources:** [S78](src.s78.md)

Until you accept the workspace trust dialog, the status line stays blank. Because `statusLine` executes a shell command, Claude Code runs it under the same workspace trust rule as hooks in settings files. Accepting the dialog for the folder, or for a parent directory whose trust extends to it, is enough.
