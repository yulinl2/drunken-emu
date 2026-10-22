---
id: cmd.focus
kind: command
status: VERIFIED
title: "/focus"
sources: [S80]
---

# /focus

**Sources:** [S80](src.s80.md)

Toggle the focus view, which shows only your last prompt, a one-line tool-call summary with edit diffstats, and the final response. The tool-call summary also counts the subagents launched in the turn and collapses completed background-task notifications into a single count. The selection persists across sessions; set `viewMode` in settings to override it. Only available in fullscreen rendering. From a Remote Control client, run `/focus [on/off]` to turn the focus view on or off for the current session only, without changing your saved selection; this requires Claude Code v2.1.281 or later. The VS Code extension offers its own Focus view as a command-menu toggle, stored as an extension setting, independent of `viewMode`
