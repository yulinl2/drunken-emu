---
id: hook-rule.http-response-handling
kind: hook-rule
status: VERIFIED
title: "HTTP response handling"
sources: [S85]
---

# HTTP response handling

**Sources:** [S85](src.s85.md)

HTTP hooks use HTTP status codes and response bodies instead of exit codes and stdout. To block the action when the request fails or returns a non-2xx status, set `onFailure: "block"`. To block a tool call or deny a permission, return a 2xx response with a JSON body containing the appropriate decision fields.
