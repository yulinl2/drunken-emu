---
id: feature.run-ultrareview-non-interactively
kind: feature
status: VERIFIED
title: "Run ultrareview non-interactively"
sources: [S23]
---

# Run ultrareview non-interactively

**Sources:** [S23](src.s23.md)

Use the `claude ultrareview` subcommand to start an ultrareview from CI or a script without an interactive session. The subcommand launches the same review as `/code-review ultra`, blocks until the remote review finishes, and prints the findings to stdout.
