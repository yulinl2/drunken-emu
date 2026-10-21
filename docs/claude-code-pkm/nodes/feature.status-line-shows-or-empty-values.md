---
id: feature.status-line-shows-or-empty-values
kind: feature
status: VERIFIED
title: "Status line shows -- or empty values"
sources: [S78]
---

# Status line shows -- or empty values

**Sources:** [S78](src.s78.md)

Fields may be `null` before the first API response completes, so handle null values in your script with fallbacks such as `// 0` in jq. Restart Claude Code if values remain empty after multiple messages.
