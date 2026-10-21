---
id: tool.glob
kind: tool
status: VERIFIED
title: "Glob"
sources: [S6, S8]
---

# Glob

**Sources:** [S6](src.s6.md), [S8](src.s8.md)

Permission: No. Finds files by pattern. Sorted by modification time, capped at 100 files, and ignores .gitignore by default. Absent by default on macOS, Linux and WSL ([Q2: Why are Glob and Grep loaded in this session?](question.q2.md)). Here: direct.

## Linked from

- [CLAUDE_CODE_GLOB_NO_IGNORE](env.claude-code-glob-no-ignore.md)
- [Q2: Why are Glob and Grep loaded in this session?](question.q2.md)
