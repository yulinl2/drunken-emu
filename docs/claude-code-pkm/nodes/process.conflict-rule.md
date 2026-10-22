---
id: process.conflict-rule
kind: process
status: DECIDED
title: "Conflict rule: best of, not union"
sources: [S2, S3, S4, S6, S7, S8, S9]
---

# Conflict rule: best of, not union

**Sources:** [S2](src.s2.md), [S3](src.s3.md), [S4](src.s4.md), [S6](src.s6.md), [S7](src.s7.md), [S8](src.s8.md), [S9](src.s9.md)

When two sources disagree, keep the one closest to the behavior being described. Record the loser as an open question with both citations. Do not merge the two claims into one row.

Priority order:

1. Live schema or official page, for what a tool or setting does: [S2: Hooks reference](src.s2.md), [S3: Settings reference](src.s3.md), [S4: CLI reference](src.s4.md), [S6: Tools reference](src.s6.md), [S7: Live deferred-tool schemas](src.s7.md).
2. This session's system prompt, for rules this session enforces: [S8: This session's system prompt and injected context](src.s8.md).
3. Repository observations, labeled by container class: [S9: Repository files](src.s9.md).
4. Prior knowledge, never on its own: [UNVERIFIED](tag.unverified.md).

Conflicts recorded so far: [Q1: Does a hook added mid-session take effect?](question.q1.md) (a hook added mid-session) and [Q2: Why are Glob and Grep loaded in this session?](question.q2.md) (Glob and Grep).
