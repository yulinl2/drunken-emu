---
id: feature.cache-lifetime
kind: feature
status: VERIFIED
title: "Cache lifetime"
sources: [S18]
---

# Cache lifetime

**Sources:** [S18](src.s18.md)

Cached prefixes expire after a period of inactivity. Each request that hits the cache resets the timer, so the cache stays warm as long as you keep working. After a long enough gap, the next request recomputes the full input and re-establishes the cache, which is why the first turn back after stepping away can be noticeably slower.
