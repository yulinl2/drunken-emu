---
id: env.claude-code-force-sync-output
kind: env
status: VERIFIED
title: "CLAUDE_CODE_FORCE_SYNC_OUTPUT"
sources: [S81]
---

# CLAUDE_CODE_FORCE_SYNC_OUTPUT

**Sources:** [S81](src.s81.md)

Set to `1` to force-enable DEC private mode 2026 synchronized output when your terminal supports it but is not auto-detected. Useful for emulators such as Emacs `eat` that implement BSU/ESU but do not reply to the capability probe. Has no effect under tmux. Unlike `CLAUDE_CODE_NO_FLICKER`, which switches to fullscreen rendering, this doesn't change the renderer
