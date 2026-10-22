---
id: feature.turn-off-screen-reader-mode
kind: feature
status: VERIFIED
title: "Turn off screen reader mode"
sources: [S76]
---

# Turn off screen reader mode

**Sources:** [S76](src.s76.md)

Reverse whichever method turned the mode on: start without the flag, unset the environment variable, or set `axScreenReader` to `false`. If you set `CLAUDE_AX_SCREEN_READER` to `0`, Claude Code keeps the mode off even when the setting is `true`.
