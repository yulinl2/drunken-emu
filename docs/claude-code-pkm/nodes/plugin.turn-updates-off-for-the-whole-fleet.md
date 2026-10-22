---
id: plugin.turn-updates-off-for-the-whole-fleet
kind: plugin
status: VERIFIED
title: "Turn updates off for the whole fleet"
sources: [S59]
---

# Turn updates off for the whole fleet

**Sources:** [S59](src.s59.md)

To turn plugin auto-update off for every marketplace, set `DISABLE_AUTOUPDATER` in the managed `env` block, as this example does. The same variable also stops Claude Code's own updates:
