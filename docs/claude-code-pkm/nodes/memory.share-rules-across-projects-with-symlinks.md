---
id: memory.share-rules-across-projects-with-symlinks
kind: memory
status: VERIFIED
title: "Share rules across projects with symlinks"
sources: [S19]
---

# Share rules across projects with symlinks

**Sources:** [S19](src.s19.md)

The `.claude/rules/` directory supports symlinks, so you can maintain a shared set of rules and link them into multiple projects. Circular symlinks are detected and handled gracefully.
