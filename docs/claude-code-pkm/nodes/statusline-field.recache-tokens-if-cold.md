---
id: statusline-field.recache-tokens-if-cold
kind: statusline-field
status: VERIFIED
title: "recache_tokens_if_cold"
sources: [S78]
---

# recache_tokens_if_cold

**Sources:** [S78](src.s78.md)

Tokens the next request re-caches if the cache has gone cold by then. `null` right after a compaction or a clearing of old tool results, until the next request records the rewritten conversation's size
