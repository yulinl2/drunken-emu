---
id: feature.changing-permission-mode
kind: feature
status: VERIFIED
title: "Changing permission mode"
sources: [S18]
---

# Changing permission mode

**Sources:** [S18](src.s18.md)

Switching between permission modes, such as from Manual to accept edits, does not change the system prompt or tool definitions, so mode changes are cache-safe. The exception is plan mode with the `opusplan` model setting, which switches the model between Opus and Sonnet as you enter or leave plan mode. That makes the mode toggle a model switch.
