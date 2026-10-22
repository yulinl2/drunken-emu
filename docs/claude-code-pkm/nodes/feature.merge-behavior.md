---
id: feature.merge-behavior
kind: feature
status: VERIFIED
title: "Merge behavior"
sources: [S70]
---

# Merge behavior

**Sources:** [S70](src.s70.md)

When the managed settings Claude Code applies define `availableModels`, that list alone applies, apart from a host platform that supplies its own: entries in user, project, or local settings cannot extend it, and Claude Code never merges `availableModels` across managed sources either; how Claude Code combines managed sources says which source's list applies. Otherwise, lists from user, project, a
