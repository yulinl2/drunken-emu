---
id: feature.actions-that-keep-the-cache
kind: feature
status: VERIFIED
title: "Actions that keep the cache"
sources: [S18]
---

# Actions that keep the cache

**Sources:** [S18](src.s18.md)

These actions either append to the end of the conversation or don't touch the request at all. Some of them, such as editing CLAUDE.md, keep the cache for the same reason the change doesn't reach the running session until `/clear`, `/compact`, or a restart.
