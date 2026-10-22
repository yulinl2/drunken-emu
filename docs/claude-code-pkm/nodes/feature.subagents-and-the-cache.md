---
id: feature.subagents-and-the-cache
kind: feature
status: VERIFIED
title: "Subagents and the cache"
sources: [S18]
---

# Subagents and the cache

**Sources:** [S18](src.s18.md)

A subagent starts its own conversation with its own system prompt and tool set, separate from the parent's. Its first request doesn't read the parent's cache, because the two prefixes differ, and it warms a cache of its own across its turns. Subagents fall outside the main-conversation TTL bucket, so they get five minutes even on a subscription until you choose a longer one.
