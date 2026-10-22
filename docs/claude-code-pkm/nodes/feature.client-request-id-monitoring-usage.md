---
id: feature.client-request-id-monitoring-usage
kind: feature
status: VERIFIED
title: "client_request_id"
sources: [S65]
---

# client_request_id

**Sources:** [S65](src.s65.md)

Client-generated UUID sent as the `x-client-request-id` request header. Present on `api_request` and `api_error` on first-party API connections; absent on third-party provider backends and when the request was retried through the non-streaming fallback. Pairs a request with its response and remains available for failures such as timeouts that never produced a server `request_id`. Matches the same attribute on the `llm_request` trace span
