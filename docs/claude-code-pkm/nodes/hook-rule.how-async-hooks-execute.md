---
id: hook-rule.how-async-hooks-execute
kind: hook-rule
status: VERIFIED
title: "How async hooks execute"
sources: [S85]
---

# How async hooks execute

**Sources:** [S85](src.s85.md)

When an async hook fires, Claude Code starts the hook process and immediately continues without waiting for it to finish. The hook receives the same JSON input via stdin as a synchronous hook.
