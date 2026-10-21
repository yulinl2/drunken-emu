---
id: mod.a-http-fetch-response-body
kind: mod
status: VERIFIED
title: "A $.http.fetch response body"
sources: [S54]
---

# A $.http.fetch response body

**Sources:** [S54](src.s54.md)

value: 4 MiB. `text` holds the first 4 MiB and the rest isn't read. When the `Content-Length` header declares more, the call rejects instead, with a reason that ends `is over the 4194304-byte limit`, except when the last request after any redirects uses the `HEAD` method. The `HEAD` exemption requires Claude Code v2.1.296 or later.
