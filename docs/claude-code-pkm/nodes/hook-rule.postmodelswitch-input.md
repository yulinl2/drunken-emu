---
id: hook-rule.postmodelswitch-input
kind: hook-rule
status: VERIFIED
title: "PostModelSwitch input"
sources: [S85]
---

# PostModelSwitch input

**Sources:** [S85](src.s85.md)

PostModelSwitch hooks receive the same fields as PreModelSwitch, with `hook_event_name` set to `"PostModelSwitch"` and two more `source` values: `"auto"` for an automatic fallback or other change Claude Code made on its own, and `"resume"` for the model restored when you resume a session.
