---
id: feature.refresh-behavior
kind: feature
status: VERIFIED
title: "Refresh behavior"
sources: [S65]
---

# Refresh behavior

**Sources:** [S65](src.s65.md)

The headers helper script runs at startup and periodically thereafter to support token refresh. By default, the script runs every 29 minutes. Customize the interval with the `CLAUDE_CODE_OTEL_HEADERS_HELPER_DEBOUNCE_MS` environment variable.
