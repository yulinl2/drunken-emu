---
id: feature.api-refusal-event
kind: feature
status: VERIFIED
title: "API refusal event"
sources: [S65]
---

# API refusal event

**Sources:** [S65](src.s65.md)

Logged when an API request returns `stop_reason: "refusal"`. Refusals arrive on a successful response stream rather than as an HTTP error, so the `api_error` event doesn't fire for them. This event lets you track refusal frequency and group refusals by the same attributes as `api_request` and `api_error`.
