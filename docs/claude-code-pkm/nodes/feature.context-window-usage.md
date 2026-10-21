---
id: feature.context-window-usage
kind: feature
status: VERIFIED
title: "Context window usage"
sources: [S78]
---

# Context window usage

**Sources:** [S78](src.s78.md)

Display the current model and context window usage with a visual progress bar. Each script reads JSON from stdin, extracts the `used_percentage` field, and builds a 10-character bar where filled blocks (▓) represent usage:
