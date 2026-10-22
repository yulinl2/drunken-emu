---
id: env.api-timeout-ms
kind: env
status: VERIFIED
title: "API_TIMEOUT_MS"
sources: [S81]
---

# API_TIMEOUT_MS

**Sources:** [S81](src.s81.md)

Time in milliseconds that each API request attempt has to receive its response headers. It doesn't limit how long a streaming response runs after that. The default is 600000, or 10 minutes, and the maximum is 2147483647. When you set a positive value, each attempt at a non-streaming request has to finish within it. Increase this when requests time out on slow networks or when routing through a proxy. Set to `0` to remove this limit, which requires Claude Code v2.1.305 or later. With `0`, a non-streaming attempt still times out after 300 seconds in a local session
