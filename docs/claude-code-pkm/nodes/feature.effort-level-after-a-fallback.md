---
id: feature.effort-level-after-a-fallback
kind: feature
status: VERIFIED
title: "Effort level after a fallback"
sources: [S70]
---

# Effort level after a fallback

**Sources:** [S70](src.s70.md)

When Claude Code switches your session to the fallback model, it keeps the effort level the flagged request ran at. For example, a session on Opus 5.5 at its default `medium` that falls back to Opus 4.8 stays at `medium`, although Opus 4.8 defaults to `high`.
