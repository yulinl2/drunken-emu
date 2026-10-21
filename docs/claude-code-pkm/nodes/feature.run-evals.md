---
id: feature.run-evals
kind: feature
status: VERIFIED
title: "Run evals"
sources: [S47]
---

# Run evals

**Sources:** [S47](src.s47.md)

Once a suite exists, `claude plugin eval` runs it. You choose which plugin and cases run with the target argument, grant any tools the cases need beyond the read-only set with `--allow-tools`, and control run count, models, cost, and output with the other options.
