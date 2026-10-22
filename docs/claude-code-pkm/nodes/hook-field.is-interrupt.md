---
id: hook-field.is-interrupt
kind: hook-field
status: VERIFIED
title: "is_interrupt"
sources: [S85]
---

# is_interrupt

**Sources:** [S85](src.s85.md)

Optional boolean. True when the failure reached Claude Code as an abort rather than as an error the tool reported. Cancelling a running tool does not fire this hook; the tool result carries the interruption message instead
