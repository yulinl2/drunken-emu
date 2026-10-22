---
id: feature.resuming-a-session
kind: feature
status: VERIFIED
title: "Resuming a session"
sources: [S18]
---

# Resuming a session

**Sources:** [S18](src.s18.md)

When you resume a session, Claude Code sends the whole conversation again, and the request reads from the cache whatever part of its prefix is unchanged and still within the cache lifetime. The layer table at the top of this page says what changes each layer.
