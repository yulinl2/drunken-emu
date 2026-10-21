---
id: feature.ask-before-switching
kind: feature
status: VERIFIED
title: "Ask before switching"
sources: [S70]
---

# Ask before switching

**Sources:** [S70](src.s70.md)

To decide what happens each time a request is flagged, run `/config`, select Switch models when a message is flagged, and choose Ask each time. You can also set `switchModelsOnFlag` to `false` in your settings file. Claude Code then pauses at a flagged request that would switch models and gives you two options: switch to the fallback model, or edit the prompt and retry.
