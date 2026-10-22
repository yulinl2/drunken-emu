---
id: permission-mode.run-in-ci-with-an-exact-allowlist
kind: permission-mode
status: VERIFIED
title: "Run in CI with an exact allowlist"
sources: [S67]
---

# Run in CI with an exact allowlist

**Sources:** [S67](src.s67.md)

Cloud sessions ignore `dontAsk` from settings files (start with: `claude -p "run the test suite" --permission-mode dontAsk --allowedTools "Bash(npm test)" "Read"`; isolation needed: None beyond what your CI runner provides)
