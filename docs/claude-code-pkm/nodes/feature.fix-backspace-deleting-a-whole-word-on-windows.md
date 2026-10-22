---
id: feature.fix-backspace-deleting-a-whole-word-on-windows
kind: feature
status: VERIFIED
title: "Fix Backspace deleting a whole word on Windows"
sources: [S74]
---

# Fix Backspace deleting a whole word on Windows

**Sources:** [S74](src.s74.md)

On Windows, Claude Code reads a Backspace that arrives as `^H` as Ctrl+Backspace, which deletes the previous word, except when `TERM_PROGRAM` is `mintty` or `TERM` is `cygwin`. On macOS and Linux, Claude Code reads it as plain Backspace.
