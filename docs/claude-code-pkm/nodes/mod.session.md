---
id: mod.session
kind: mod
status: VERIFIED
title: "$.session"
sources: [S54]
---

# $.session

**Sources:** [S54](src.s54.md)

methods: `messages`, `cwd`, `root`, `model`, `turns`, `id`, `repo`, `surfaces`, `usage`, `version`, `compact`, `send`, `append`, `authorize`. `usage()` returns `{ startedAt, context, rateLimits, cost }`: `context` has `tokens`, `window`, and `percent`, and `rateLimits` is a list of `{ kind, percentUsed, resetsAt }`.
