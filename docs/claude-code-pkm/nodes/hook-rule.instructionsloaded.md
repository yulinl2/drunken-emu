---
id: hook-rule.instructionsloaded
kind: hook-rule
status: VERIFIED
title: "InstructionsLoaded"
sources: [S85]
---

# InstructionsLoaded

**Sources:** [S85](src.s85.md)

Fires when a `CLAUDE.md` or `.claude/rules/*.md` file is loaded into context. This event fires at session start for eagerly loaded files and again later when files are lazily loaded, for example when Claude accesses a subdirectory that contains a nested `CLAUDE.md` or when conditional rules with `paths:` frontmatter match. The hook doesn't support blocking or decision control. It runs asynchronous
