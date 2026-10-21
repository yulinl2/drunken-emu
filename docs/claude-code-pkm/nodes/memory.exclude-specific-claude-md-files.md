---
id: memory.exclude-specific-claude-md-files
kind: memory
status: VERIFIED
title: "Exclude specific CLAUDE.md files"
sources: [S19]
---

# Exclude specific CLAUDE.md files

**Sources:** [S19](src.s19.md)

In large monorepos, ancestor CLAUDE.md files may contain instructions that aren't relevant to your work. The `claudeMdExcludes` setting lets you skip specific files by path or glob pattern. You can't exclude a managed CLAUDE.md file with `claudeMdExcludes`.
