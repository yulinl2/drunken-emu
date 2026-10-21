---
id: cli.hasuserconfig
kind: cli
status: VERIFIED
title: "hasUserConfig"
sources: [S52]
---

# hasUserConfig

**Sources:** [S52](src.s52.md)

Present and `true` when the plugin loaded and its manifest declares `userConfig` options. Absent for a plugin that failed to load, whatever its manifest declares. Saved values are never included. Requires Claude Code v2.1.285 or later (type: boolean)
