---
id: feature.mouse-wheel-scrolling
kind: feature
status: VERIFIED
title: "Mouse wheel scrolling"
sources: [S75]
---

# Mouse wheel scrolling

**Sources:** [S75](src.s75.md)

Mouse wheel scrolling requires your terminal to forward mouse events to Claude Code. Most terminals do this whenever an application requests it. iTerm2 makes it a per-profile setting: if the wheel does nothing but `PgUp` and `PgDn` work, open Settings → Profiles → Terminal and turn on Enable mouse reporting. The same setting is also required for click-to-expand and text selection to work.
