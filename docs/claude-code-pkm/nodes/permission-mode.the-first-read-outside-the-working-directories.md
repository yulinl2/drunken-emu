---
id: permission-mode.the-first-read-outside-the-working-directories
kind: permission-mode
status: VERIFIED
title: "The first read outside the working directories"
sources: [S67]
---

# The first read outside the working directories

**Sources:** [S67](src.s67.md)

While `permissions.blockReadsOutsideWorkingDirectories` is off, file reads other than reads from network paths run without a prompt in auto mode, including reads outside the working directories. The first time Claude uses the Read, Grep, or Glob tool on a path outside them, Claude Code asks whether to allow that read.
