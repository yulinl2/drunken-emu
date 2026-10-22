---
id: feature.what-persists-across-restarts
kind: feature
status: VERIFIED
title: "What persists across restarts"
sources: [S26]
---

# What persists across restarts

**Sources:** [S26](src.s26.md)

The permission mode, model, and effort you chose for a background session, along with the configuration flags it carries, all persist when the supervisor later stops and restarts its process. A model or effort you changed mid-session with `/model` or `/effort` is kept too.
