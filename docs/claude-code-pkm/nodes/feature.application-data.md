---
id: feature.application-data
kind: feature
status: VERIFIED
title: "Application data"
sources: [S16]
---

# Application data

**Sources:** [S16](src.s16.md)

Beyond the config you author, `~/.claude` holds data Claude Code writes during sessions. These files are plaintext. Anything that passes through a tool is written to a transcript on disk: file contents, command output, pasted text.
