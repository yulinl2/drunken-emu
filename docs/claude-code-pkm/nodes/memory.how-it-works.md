---
id: memory.how-it-works
kind: memory
status: VERIFIED
title: "How it works"
sources: [S19]
---

# How it works

**Sources:** [S19](src.s19.md)

The first 200 lines of `MEMORY.md`, or the first 25KB, whichever comes first, are loaded at the start of every conversation. Content beyond that threshold is not loaded at session start. Claude keeps `MEMORY.md` concise by moving detailed notes into separate topic files.
