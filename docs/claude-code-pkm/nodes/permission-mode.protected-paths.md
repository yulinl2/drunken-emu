---
id: permission-mode.protected-paths
kind: permission-mode
status: VERIFIED
title: "Protected paths"
sources: [S67]
---

# Protected paths

**Sources:** [S67](src.s67.md)

Writes to a small set of paths are never auto-approved, except in `bypassPermissions` mode and in interactive terminal sessions in plan mode with bypass permissions available. This prevents accidental corruption of repository state and Claude's own configuration.
