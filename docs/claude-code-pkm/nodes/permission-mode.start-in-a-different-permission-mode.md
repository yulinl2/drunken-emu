---
id: permission-mode.start-in-a-different-permission-mode
kind: permission-mode
status: VERIFIED
title: "Start in a different permission mode"
sources: [S67]
---

# Start in a different permission mode

**Sources:** [S67](src.s67.md)

You can set the starting permission mode for one session, or as a default for every session on a machine, in a project, or in an organization. When more than one settings file sets `permissions.defaultMode`, settings precedence decides, so a project or managed value outranks `~/.claude/settings.json`. To change the permission mode of a session that's already running, see Switch permission modes.
