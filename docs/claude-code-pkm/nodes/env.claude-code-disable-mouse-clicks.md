---
id: env.claude-code-disable-mouse-clicks
kind: env
status: VERIFIED
title: "CLAUDE_CODE_DISABLE_MOUSE_CLICKS"
sources: [S81]
---

# CLAUDE_CODE_DISABLE_MOUSE_CLICKS

**Sources:** [S81](src.s81.md)

Set to `1` to disable click, drag, and hover handling in fullscreen rendering while keeping mouse-wheel scrolling. Use this when you want wheel scroll to work inside Claude Code but don't want clicks to position the cursor, expand tool output, or open links. `CLAUDE_CODE_DISABLE_MOUSE` takes precedence when both are set. Requires Claude Code v2.1.195 or later
