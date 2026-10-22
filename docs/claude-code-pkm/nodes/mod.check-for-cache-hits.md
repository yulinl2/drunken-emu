---
id: mod.check-for-cache-hits
kind: mod
status: VERIFIED
title: "Check for cache hits"
sources: [S56]
---

# Check for cache hits

**Sources:** [S56](src.s56.md)

The result of `$.model.complete` has a `usage` object with the API's cache fields. `usage.cache_creation_input_tokens` counts the tokens the call wrote to the cache, and `usage.cache_read_input_tokens` counts the tokens it read from the cache. Expect a write on the first call and reads on later calls within the TTL.
