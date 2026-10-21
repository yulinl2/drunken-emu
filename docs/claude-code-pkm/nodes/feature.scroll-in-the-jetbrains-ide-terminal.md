---
id: feature.scroll-in-the-jetbrains-ide-terminal
kind: feature
status: VERIFIED
title: "Scroll in the JetBrains IDE terminal"
sources: [S75]
---

# Scroll in the JetBrains IDE terminal

**Sources:** [S75](src.s75.md)

In the JetBrains IDE terminal, Claude Code applies its own scroll handling and ignores `CLAUDE_CODE_SCROLL_SPEED`. The terminal sends scroll events at a much higher rate than other emulators, so a multiplier tuned elsewhere overshoots here.
