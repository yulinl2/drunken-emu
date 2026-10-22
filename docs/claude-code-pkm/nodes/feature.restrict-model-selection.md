---
id: feature.restrict-model-selection
kind: feature
status: VERIFIED
title: "Restrict model selection"
sources: [S70]
---

# Restrict model selection

**Sources:** [S70](src.s70.md)

Administrators can use `availableModels` in managed or policy settings to restrict which models users can select. Entries match a model family such as `sonnet`, a version prefix such as `claude-sonnet-4-5`, or a full model ID such as `claude-sonnet-4-5-20250929`. A version prefix also matches later model IDs that extend it with another segment, so `claude-fable-5` permits both Fable 5 and Fable 5.
