---
id: feature.detect-retry-exhaustion
kind: feature
status: VERIFIED
title: "Detect retry exhaustion"
sources: [S65]
---

# Detect retry exhaustion

**Sources:** [S65](src.s65.md)

Claude Code retries failed API requests internally and emits a single `claude_code.api_error` event only after it gives up, so the event itself is the terminal signal for that request. Intermediate retry attempts are not logged as separate events.
