---
id: feature.fix-repeated-denials
kind: feature
status: VERIFIED
title: "Fix repeated denials"
sources: [S64]
---

# Fix repeated denials

**Sources:** [S64](src.s64.md)

Repeated denials for the same destination usually mean the classifier is missing context. Add that destination to `autoMode.environment`, or run `/auto-mode-setup` to have Claude Code draft the entries, then run `claude auto-mode config` to confirm the change took effect.
