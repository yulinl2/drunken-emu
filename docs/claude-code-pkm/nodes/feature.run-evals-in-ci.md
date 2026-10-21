---
id: feature.run-evals-in-ci
kind: feature
status: VERIFIED
title: "Run evals in CI"
sources: [S47]
---

# Run evals in CI

**Sources:** [S47](src.s47.md)

In your CI job, run the suite with `--json` to write the result for archiving, and fail the build on the exit code. Pass `--trust-plugin` so the job never waits at the first-run trust prompt, pin both models so scores are comparable over time, keep the report local, and set a cost ceiling as an upper limit:
