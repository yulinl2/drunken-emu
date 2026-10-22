---
id: memory.storage-location
kind: memory
status: VERIFIED
title: "Storage location"
sources: [S19]
---

# Storage location

**Sources:** [S19](src.s19.md)

Each project gets its own memory directory at `~/.claude/projects//memory/`. The `` path is derived from the git repository, so all worktrees and subdirectories within the same repo share one auto memory directory. Outside a git repo, the project root is used instead.
