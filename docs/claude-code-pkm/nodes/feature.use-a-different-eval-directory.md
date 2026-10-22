---
id: feature.use-a-different-eval-directory
kind: feature
status: VERIFIED
title: "Use a different eval directory"
sources: [S47]
---

# Use a different eval directory

**Sources:** [S47](src.s47.md)

If `evals/` is already taken by another tool, keep the suite in a different directory. You can record that directory in the plugin's `plugin.json` so every run and every collaborator uses it, or pass it on the command line for a single run:
