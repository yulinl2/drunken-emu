---
id: feature.turning-on-fast-mode
kind: feature
status: VERIFIED
title: "Turning on fast mode"
sources: [S18]
---

# Turning on fast mode

**Sources:** [S18](src.s18.md)

Enabling fast mode adds a request header that is part of the cache key, so the first request Claude Code sends with fast mode on reads the entire conversation history with no cache hits. Claude Code sets that header once when a turn starts and keeps it for the whole turn, so when you turn fast mode on while Claude is working, the cache miss from the header happens on the first request of your next
