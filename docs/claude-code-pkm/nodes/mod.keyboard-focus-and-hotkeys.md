---
id: mod.keyboard-focus-and-hotkeys
kind: mod
status: VERIFIED
title: "Keyboard focus and hotkeys"
sources: [S57]
---

# Keyboard focus and hotkeys

**Sources:** [S57](src.s57.md)

Your mod never reads the keyboard itself. The user presses a key, Claude Code decides which of your controls it's for, and that control's callback runs. Apart from a digit hotkey on the band, that happens only while your pane or band has keyboard focus. The rest of the time, keys go to the prompt.
