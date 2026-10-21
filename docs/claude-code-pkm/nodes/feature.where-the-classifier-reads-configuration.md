---
id: feature.where-the-classifier-reads-configuration
kind: feature
status: VERIFIED
title: "Where the classifier reads configuration"
sources: [S64]
---

# Where the classifier reads configuration

**Sources:** [S64](src.s64.md)

The classifier reads the same CLAUDE.md content Claude itself loads, so an instruction like "never force push" in your project's CLAUDE.md steers both Claude and the classifier at the same time. Start there for project conventions and behavioral rules.
