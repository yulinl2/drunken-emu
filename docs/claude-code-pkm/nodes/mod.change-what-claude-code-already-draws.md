---
id: mod.change-what-claude-code-already-draws
kind: mod
status: VERIFIED
title: "Change what Claude Code already draws"
sources: [S57]
---

# Change what Claude Code already draws

**Sources:** [S57](src.s57.md)

Claude Code draws most of its interface itself: messages, tool call rows, the spinner, and more. Each of those parts is a render site too, so a mod can restyle or replace it. To change one, filter your `ui.render` hook on its name from this table:
