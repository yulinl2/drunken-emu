---
id: permission-mode.some-targets-that-end-in-or
kind: permission-mode
status: VERIFIED
title: "Some targets that end in /* or /*/"
sources: [S67]
---

# Some targets that end in /* or /*/

**Sources:** [S67](src.s67.md)

example: `rm -rf logs/*/*`, `rm -rf logs/*/`, `cd logs && rm -rf a/*`; why it counts: Claude Code can't tell before the command runs which directories they reach
