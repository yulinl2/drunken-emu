---
id: feature.enable-fullscreen-rendering
kind: feature
status: VERIFIED
title: "Enable fullscreen rendering"
sources: [S75]
---

# Enable fullscreen rendering

**Sources:** [S75](src.s75.md)

Run `/tui fullscreen` inside any Claude Code conversation. The CLI saves the `tui` setting and relaunches into fullscreen with your conversation intact, so you can switch mid-session without losing context. Run `/tui default` to switch back to the classic renderer, or `/tui` with no argument to print which renderer is active.
