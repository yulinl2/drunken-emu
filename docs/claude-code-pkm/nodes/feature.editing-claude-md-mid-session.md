---
id: feature.editing-claude-md-mid-session
kind: feature
status: VERIFIED
title: "Editing CLAUDE.md mid-session"
sources: [S18]
---

# Editing CLAUDE.md mid-session

**Sources:** [S18](src.s18.md)

Your project-root and user-level CLAUDE.md files are read once at session start and held in memory. Editing them mid-session does not invalidate the cache, but the edit also doesn't apply. Claude keeps working with the version that was loaded at session start. The new content loads on the next `/clear`, `/compact`, or restart.
