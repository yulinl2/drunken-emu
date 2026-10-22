---
id: env.claude-code-scroll-speed
kind: env
status: VERIFIED
title: "CLAUDE_CODE_SCROLL_SPEED"
sources: [S81]
---

# CLAUDE_CODE_SCROLL_SPEED

**Sources:** [S81](src.s81.md)

Set the mouse wheel scroll multiplier in fullscreen rendering. Accepts any positive value up to 20, including fractional values below 1 such as `0.5` to slow accelerated trackpad and wheel scrolling in terminals that already amplify wheel events. Set to `3` to match `vim` if your terminal sends one wheel event per notch without amplification. Ignored in the JetBrains IDE terminal, where Claude Code uses its own scroll handling
