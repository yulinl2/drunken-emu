---
id: hook-field.transcript-path
kind: hook-field
status: VERIFIED
title: "transcript_path"
sources: [S85]
---

# transcript_path

**Sources:** [S85](src.s85.md)

Path to conversation JSON. The transcript file is written asynchronously and may lag the in-memory conversation, so it may not yet include the current turn's most recent messages when a hook fires. Hooks that need the final assistant text of the current turn should use `last_assistant_message` on Stop and SubagentStop instead of reading the transcript
