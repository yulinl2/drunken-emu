---
id: tool.glob-tool-behavior
kind: tool
status: VERIFIED
title: "Glob tool behavior"
sources: [S82]
---

# Glob tool behavior

**Sources:** [S82](src.s82.md)

The Glob tool finds files by name pattern. On Windows, it's part of the default tool set. On macOS, Linux, and WSL, Claude Code leaves Glob and Grep out of the default tool set, and Claude searches with `find` and `grep` through the Bash tool instead. In Claude's shell those two commands run embedded versions of `bfs` and `ugrep`, and the searches reach your hooks and permission rules as `Bash` ca
