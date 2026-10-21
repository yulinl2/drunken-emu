---
id: feature.request-id-monitoring-usage-2
kind: feature
status: VERIFIED
title: "request_id"
sources: [S65]
---

# request_id

**Sources:** [S65](src.s65.md)

Server-assigned ID of the API request, read from the `request-id` response header, such as `req_011...`. On a response with no `request-id` header, as on Amazon Bedrock, the value comes from the `x-amzn-requestid` header instead. Present on `api_request`, `api_error`, `api_refusal`, `assistant_response`, and `api_response_body` when the response carries either header. Matches the same attribute on the `llm_request` trace span. The `x-amzn-requestid` source requires Claude Code v2.1.282 or later
