---
id: env.claude-code-disable-alternate-screen
kind: env
status: VERIFIED
title: "CLAUDE_CODE_DISABLE_ALTERNATE_SCREEN"
sources: [S81]
---

# CLAUDE_CODE_DISABLE_ALTERNATE_SCREEN

**Sources:** [S81](src.s81.md)

Set to `1` to disable fullscreen rendering and use the classic main-screen renderer. The conversation stays in your terminal's native scrollback so `Cmd+f` and tmux copy mode work as usual. Takes precedence over `CLAUDE_CODE_NO_FLICKER` and the `tui` setting. You can also switch with `/tui default`. Does not apply to background sessions opened from agent view, which always use fullscreen rendering
