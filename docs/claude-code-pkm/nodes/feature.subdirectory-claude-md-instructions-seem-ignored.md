---
id: feature.subdirectory-claude-md-instructions-seem-ignored
kind: feature
status: VERIFIED
title: "Subdirectory CLAUDE.md instructions seem ignored"
sources: [S40]
---

# Subdirectory CLAUDE.md instructions seem ignored

**Sources:** [S40](src.s40.md)

cause: Subdirectory files load on demand, not at session start; fix: To load a subdirectory's `CLAUDE.md`, ask Claude to read another file in that subdirectory. See when subdirectory files load.
