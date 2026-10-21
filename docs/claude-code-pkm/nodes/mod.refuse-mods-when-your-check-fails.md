---
id: mod.refuse-mods-when-your-check-fails
kind: mod
status: VERIFIED
title: "Refuse mods when your check fails"
sources: [S58]
---

# Refuse mods when your check fails

**Sources:** [S58](src.s58.md)

If your `plugin.register` hook throws or exceeds its time limit, Claude Code skips the hook, so the check fails open and the mod it was checking loads. To fail closed and refuse users' mods, move the check into a named function and add a `.catch` handler that returns the refusal. This version of the file shows the `plugin.register` hook only, so keep the two audit hooks from the first version in `
