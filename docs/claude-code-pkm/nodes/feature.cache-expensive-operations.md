---
id: feature.cache-expensive-operations
kind: feature
status: VERIFIED
title: "Cache expensive operations"
sources: [S78]
---

# Cache expensive operations

**Sources:** [S78](src.s78.md)

Your status line script runs frequently during active sessions. Commands like `git status` or `git diff` can be slow, especially in large repositories. This example caches git information to a temp file and only refreshes it every 5 seconds.
