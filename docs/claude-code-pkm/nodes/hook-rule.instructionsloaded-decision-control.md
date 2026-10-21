---
id: hook-rule.instructionsloaded-decision-control
kind: hook-rule
status: VERIFIED
title: "InstructionsLoaded decision control"
sources: [S85]
---

# InstructionsLoaded decision control

**Sources:** [S85](src.s85.md)

InstructionsLoaded hooks have no decision control. They can't block or modify instruction loading. Claude Code discards their JSON output fields, such as `systemMessage` and `continue`. Use this event for audit logging, compliance tracking, or observability.
