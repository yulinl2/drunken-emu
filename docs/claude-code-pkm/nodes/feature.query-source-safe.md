---
id: feature.query-source-safe
kind: feature
status: VERIFIED
title: "query_source_safe"
sources: [S65]
---

# query_source_safe

**Sources:** [S65](src.s65.md)

Bounded form of `query_source`, emitted whether or not detailed beta tracing is active, with values such as `repl_main_thread` or `agent.builtin.general-purpose`. `:` becomes `.` and user-named agents appear as `agent.custom`. Requires Claude Code v2.1.268 or later
