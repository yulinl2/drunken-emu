---
id: feature.cache-scope
kind: feature
status: VERIFIED
title: "Cache scope"
sources: [S18]
---

# Cache scope

**Sources:** [S18](src.s18.md)

In Claude Code, the cache is effectively scoped to one machine and directory. The system prompt embeds your auto memory paths, and the conversation opens with an announcement of the working directory, platform, shell, and OS version. Two sessions in different directories therefore build different prefixes and miss each other's cache.
