---
id: feature.rewinding-the-conversation
kind: feature
status: VERIFIED
title: "Rewinding the conversation"
sources: [S18]
---

# Rewinding the conversation

**Sources:** [S18](src.s18.md)

`/rewind` truncates your conversation back to an earlier turn. The remaining history is the same content the cache was built from at that point, and the system prompt and project context layers are unchanged, so the next request hits the earlier cache entry. Every turn since then has read through that prefix, which kept the entry warm even if the original turn was longer ago than the TTL.
