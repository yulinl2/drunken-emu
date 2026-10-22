---
id: mod.keep-a-value-in-state
kind: mod
status: VERIFIED
title: "Keep a value in $.state"
sources: [S57]
---

# Keep a value in $.state

**Sources:** [S57](src.s57.md)

`$.state` holds values for the length of a session, and it redraws for you. It's reactive state: a `ui.render` hook that reads a value subscribes to it, so Claude Code redraws that site each time you write the value, and you don't call `$.ui.invalidate`. A value in `$.state` also survives a reload of the module, which a variable doesn't.
