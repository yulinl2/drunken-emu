---
id: feature.keep-native-text-selection
kind: feature
status: VERIFIED
title: "Keep native text selection"
sources: [S75]
---

# Keep native text selection

**Sources:** [S75](src.s75.md)

Mouse capture is the most common friction point, especially over SSH or inside tmux. When Claude Code captures mouse events, your terminal's native copy-on-select stops working. The selection you make with click-and-drag exists inside Claude Code, not in your terminal's selection buffer, so tmux copy mode, Kitty hints, and similar tools don't see it.
