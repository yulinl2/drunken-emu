---
id: feature.temporary-directories
kind: feature
status: VERIFIED
title: "Temporary directories"
sources: [S68]
---

# Temporary directories

**Sources:** [S68](src.s68.md)

A per-user temp directory is writable inside the sandbox by default, alongside the working directory. Unless you disable filesystem isolation, Claude Code sets `$TMPDIR` to this directory for sandboxed commands, so tools that write temporary files work without extra configuration.
