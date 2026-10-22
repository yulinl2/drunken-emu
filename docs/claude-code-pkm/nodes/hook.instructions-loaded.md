---
id: hook.instructions-loaded
kind: hook
status: VERIFIED
title: "InstructionsLoaded"
sources: [S2]
---

# InstructionsLoaded

**Sources:** [S2](src.s2.md)

Fires when CLAUDE.md or .claude/rules/*.md enters context. Matchers: session_start, nested_traversal, path_glob_match, include, compact. Side effects only. See [CLAUDE.md](memory.claude-md.md).

## Linked from

- [.claude/rules/*.md](memory.rules-dir.md)
- [Load reason: session_start](memory.load-reason-session-start.md)
