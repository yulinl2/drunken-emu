---
id: feature.check-cache-performance
kind: feature
status: VERIFIED
title: "Check cache performance"
sources: [S18]
---

# Check cache performance

**Sources:** [S18](src.s18.md)

Cache performance shows up as two token counts the API reports on every response. The most direct way to watch them live is a statusline script that reads the `current_usage` object:
