---
id: hook-field.estimated-cache-write-usd-hooks
kind: hook-field
status: VERIFIED
title: "estimated_cache_write_usd"
sources: [S85]
---

# estimated_cache_write_usd

**Sources:** [S85](src.s85.md)

Estimated cost in US dollars of writing `context_tokens` to the prompt cache on `to_model` at the `cache_ttl` rate, excluding the next response. The server may not need to re-cache the whole context, so treat it as an estimate (type: number)
