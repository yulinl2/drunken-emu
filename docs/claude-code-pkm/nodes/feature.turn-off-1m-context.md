---
id: feature.turn-off-1m-context
kind: feature
status: VERIFIED
title: "Turn off 1M context"
sources: [S70]
---

# Turn off 1M context

**Sources:** [S70](src.s70.md)

To keep sessions at a 200K window, set `CLAUDE_CODE_DISABLE_1M_CONTEXT=1` in your shell or in a settings file. Claude Code removes the `[1m]` model variants from the model picker. On models that run with the 1M window by default, such as the Fable models, Sonnet 5 and later, and Opus 4.7 and later, it also treats the model as having a 200K context window:
