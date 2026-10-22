---
id: feature.the-no-plugin-baseline
kind: feature
status: VERIFIED
title: "The no-plugin baseline"
sources: [S47]
---

# The no-plugin baseline

**Sources:** [S47](src.s47.md)

A high score on its own doesn't tell you the plugin helped, because Claude might do as well without it. To separate the two, a case's runs are repeated with no plugin loaded, and you get two scores, `WITH` and `W/OUT`. Their difference, `Δ`, is what the plugin contributed. If a case scores 1.0 both with and without the plugin, the plugin isn't what made it pass.
