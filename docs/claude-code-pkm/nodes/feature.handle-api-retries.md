---
id: feature.handle-api-retries
kind: feature
status: VERIFIED
title: "Handle API retries"
sources: [S38]
---

# Handle API retries

**Sources:** [S38](src.s38.md)

When an API request fails with a retryable error, Claude Code emits a `system/api_retry` event before retrying. On v2.1.246 or later, when a `401` or `403` rejects an `apiKeyHelper` credential, Claude Code makes the first two retries quietly with no event, then emits the event as usual from the third consecutive retry onward. The quiet retries still count toward `attempt`. You can use the event to
