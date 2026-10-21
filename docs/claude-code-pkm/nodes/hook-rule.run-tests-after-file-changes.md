---
id: hook-rule.run-tests-after-file-changes
kind: hook-rule
status: VERIFIED
title: "Run tests after file changes"
sources: [S85]
---

# Run tests after file changes

**Sources:** [S85](src.s85.md)

This hook starts a test suite in the background whenever Claude writes a file, then reports the results back to Claude when the tests finish. Save this script to `.claude/hooks/run-tests-async.sh` in your project and make it executable with `chmod +x`:
