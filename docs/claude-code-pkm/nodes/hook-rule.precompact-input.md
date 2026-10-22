---
id: hook-rule.precompact-input
kind: hook-rule
status: VERIFIED
title: "PreCompact input"
sources: [S85]
---

# PreCompact input

**Sources:** [S85](src.s85.md)

In addition to the common input fields, PreCompact hooks receive `trigger` and `custom_instructions`. For `manual`, `custom_instructions` contains what the user passes into `/compact` and is `null` when they pass nothing. For `auto`, `custom_instructions` is `null`.
