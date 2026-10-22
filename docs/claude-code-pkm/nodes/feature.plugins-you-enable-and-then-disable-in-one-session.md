---
id: feature.plugins-you-enable-and-then-disable-in-one-session
kind: feature
status: VERIFIED
title: "Plugins you enable and then disable in one session"
sources: [S18]
---

# Plugins you enable and then disable in one session

**Sources:** [S18](src.s18.md)

When you disable a plugin you enabled earlier in the session, Claude Code restores the previous request shape. If that prefix is still within its cache lifetime, the next request reads the older cache entry instead of rebuilding.
