---
id: memory.my-agents-md-isn-t-loading
kind: memory
status: VERIFIED
title: "My AGENTS.md isn't loading"
sources: [S19]
---

# My AGENTS.md isn't loading

**Sources:** [S19](src.s19.md)

If your repository has an `AGENTS.md` and Claude doesn't seem to know what it says, the usual cause is a `CLAUDE.md` somewhere on the project path. By default Claude reads `AGENTS.md` only when you have no `CLAUDE.md` or `CLAUDE.local.md` in your working directory or above it. Check these in order:
