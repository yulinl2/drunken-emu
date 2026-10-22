---
id: statusline-field.hit-ratio
kind: statusline-field
status: VERIFIED
title: "hit_ratio"
sources: [S78]
---

# hit_ratio

**Sources:** [S78](src.s78.md)

Cache read tokens as a fraction of all input tokens this session, from 0 to 1. The denominator counts cache reads, cache writes, and uncached input. `null` while those counts are all zero
