---
id: hook-field.session-title
kind: hook-field
status: VERIFIED
title: "session_title"
sources: [S85]
---

# session_title

**Sources:** [S85](src.s85.md)

The session's custom title, present when one is set, for example with `--name`, `/rename`, a hook's `sessionTitle` output, or the Agent SDK's `renameSession()`. A hook that emits `sessionTitle` can check this field first to avoid overwriting an existing custom title
