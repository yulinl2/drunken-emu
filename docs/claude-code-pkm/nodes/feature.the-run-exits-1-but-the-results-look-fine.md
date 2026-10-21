---
id: feature.the-run-exits-1-but-the-results-look-fine
kind: feature
status: VERIFIED
title: "The run exits 1 but the results look fine"
sources: [S47]
---

# The run exits 1 but the results look fine

**Sources:** [S47](src.s47.md)

When every case scored at or above `--threshold` and the command still exits 1, a line on stderr names the cause, even under `--json`. For example, a case file failed to load, or runs ended on an API error. For the other causes, see the exit codes.
