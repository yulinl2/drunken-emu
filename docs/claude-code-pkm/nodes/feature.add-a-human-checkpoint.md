---
id: feature.add-a-human-checkpoint
kind: feature
status: VERIFIED
title: "Add a human checkpoint"
sources: [S64]
---

# Add a human checkpoint

**Sources:** [S64](src.s64.md)

The most direct mechanism is `permissions.ask`. Content-scoped ask rules like the ones below are evaluated before the classifier and always force a permission prompt, even in auto mode, because an explicit ask rule is your stated intent to be prompted for that action. Add the rules in your settings:
