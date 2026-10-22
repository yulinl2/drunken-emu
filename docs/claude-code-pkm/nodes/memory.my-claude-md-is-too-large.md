---
id: memory.my-claude-md-is-too-large
kind: memory
status: VERIFIED
title: "My CLAUDE.md is too large"
sources: [S19]
---

# My CLAUDE.md is too large

**Sources:** [S19](src.s19.md)

Files over 200 lines consume more context and may reduce adherence. Claude Code skips a file over 4 MiB. Use path-scoped rules to load instructions only when Claude works with matching files, or trim content that isn't needed in every session. Splitting into `@path` imports helps organization but doesn't reduce context, since imported files load at launch.
