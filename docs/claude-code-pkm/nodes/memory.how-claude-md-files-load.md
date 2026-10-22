---
id: memory.how-claude-md-files-load
kind: memory
status: VERIFIED
title: "How CLAUDE.md files load"
sources: [S19]
---

# How CLAUDE.md files load

**Sources:** [S19](src.s19.md)

Claude Code loads `CLAUDE.md` and `CLAUDE.local.md` from your current working directory and every directory above it. Run Claude Code in `foo/bar/` and it loads instructions from `foo/bar/CLAUDE.md`, `foo/CLAUDE.md`, and any `CLAUDE.local.md` files alongside them.
