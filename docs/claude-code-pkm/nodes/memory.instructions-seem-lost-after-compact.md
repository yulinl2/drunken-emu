---
id: memory.instructions-seem-lost-after-compact
kind: memory
status: VERIFIED
title: "Instructions seem lost after /compact"
sources: [S19]
---

# Instructions seem lost after /compact

**Sources:** [S19](src.s19.md)

Project-root CLAUDE.md survives compaction: after `/compact`, Claude re-reads it from disk and re-injects it into the session. Nested CLAUDE.md files in subdirectories and rules with `paths:` frontmatter load again on demand.
