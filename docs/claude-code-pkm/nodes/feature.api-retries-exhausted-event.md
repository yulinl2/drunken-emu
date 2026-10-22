---
id: feature.api-retries-exhausted-event
kind: feature
status: VERIFIED
title: "API retries exhausted event"
sources: [S65]
---

# API retries exhausted event

**Sources:** [S65](src.s65.md)

Logged once when an API request fails after more than one attempt. Emitted alongside the final `api_error` event.
