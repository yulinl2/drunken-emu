---
id: memory.claude-md-vs-auto-memory
kind: memory
status: VERIFIED
title: "CLAUDE.md vs auto memory"
sources: [S19]
---

# CLAUDE.md vs auto memory

**Sources:** [S19](src.s19.md)

Claude Code has two complementary memory systems. Both are loaded at the start of every conversation. Claude treats them as context, not enforced configuration. To block an action regardless of what Claude decides, use a PreToolUse hook instead. The more specific and concise your instructions, the more consistently Claude follows them.
