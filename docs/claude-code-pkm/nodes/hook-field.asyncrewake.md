---
id: hook-field.asyncrewake
kind: hook-field
status: VERIFIED
title: "asyncRewake"
sources: [S85]
---

# asyncRewake

**Sources:** [S85](src.s85.md)

If `true`, runs in the background and wakes Claude on exit code 2. The hook's stderr, or stdout if stderr is empty, is shown to Claude as a system reminder so it can react to a long-running background failure (required: no)
