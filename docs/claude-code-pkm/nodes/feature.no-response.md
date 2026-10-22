---
id: feature.no-response
kind: feature
status: VERIFIED
title: "no_response"
sources: [S38]
---

# no_response

**Sources:** [S38](src.s38.md)

present only when the failed attempt got no response headers in time. `waited_ms` is how long that attempt waited and `retry_wait_ms` is how long the retry will wait. Requires Claude Code v2.1.261 or later (type: object, optional)
