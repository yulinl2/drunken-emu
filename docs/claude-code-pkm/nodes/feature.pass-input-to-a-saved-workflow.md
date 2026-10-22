---
id: feature.pass-input-to-a-saved-workflow
kind: feature
status: VERIFIED
title: "Pass input to a saved workflow"
sources: [S29]
---

# Pass input to a saved workflow

**Sources:** [S29](src.s29.md)

A saved workflow can accept input through the `args` parameter. The script reads it as a global named `args`. Use this to supply a research question, a list of target paths, or a configuration object at invocation time instead of editing the script for each run.
