---
id: question.q2
kind: question
status: OPEN
title: "Q2: Why are Glob and Grep loaded in this session?"
sources: [S6, S8]
---

# Q2: Why are Glob and Grep loaded in this session?

**Sources:** [S6](src.s6.md), [S8](src.s8.md)

[Glob](tool.glob.md) and [Grep](tool.grep.md) are absent by default on macOS, Linux and WSL, according to the tools reference. Naming either in [--tools](flag.tools.md) or [--allowedTools (alias --allowed-tools)](flag.allowed-tools.md) restores them. This session lists both as direct tools ([S8: This session's system prompt and injected context](src.s8.md)). Next check: find the surface's --tools setting, which is not visible from inside the session.

## Linked from

- [--tools](flag.tools.md)
- [Conflict rule: best of, not union](process.conflict-rule.md)
- [Glob](tool.glob.md)
- [Grep](tool.grep.md)
- [This session (2026-10-21)](environment.this-session.md)
