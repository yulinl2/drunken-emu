---
id: feature.choose-what-to-evaluate
kind: feature
status: VERIFIED
title: "Choose what to evaluate"
sources: [S47]
---

# Choose what to evaluate

**Sources:** [S47](src.s47.md)

Most of the time you run `claude plugin eval .` from the plugin root, which runs every case in the suite with the plugin you're standing in loaded. To run a single case file, or to evaluate a plugin you installed rather than one you're developing, pass a different target:
