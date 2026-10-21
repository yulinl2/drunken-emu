---
id: mod.load-a-saved-value-again-after-clear
kind: mod
status: VERIFIED
title: "Load a saved value again after /clear"
sources: [S57]
---

# Load a saved value again after /clear

**Sources:** [S57](src.s57.md)

If your mod copies a saved value from `$.store` into `$.state` at `session.start`, it has to copy it again after `/clear`, `/resume`, or `/branch`. Those commands reset every `$.state` value to its default, and `session.start` doesn't fire again. `classic.SessionStart` does fire after each of them, with `e.source` set to `clear`, `resume`, or `fork`, so copy the value again in a hook on it. Otherw
