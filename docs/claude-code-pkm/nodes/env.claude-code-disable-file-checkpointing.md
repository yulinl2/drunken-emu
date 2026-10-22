---
id: env.claude-code-disable-file-checkpointing
kind: env
status: VERIFIED
title: "CLAUDE_CODE_DISABLE_FILE_CHECKPOINTING"
sources: [S81]
---

# CLAUDE_CODE_DISABLE_FILE_CHECKPOINTING

**Sources:** [S81](src.s81.md)

Set to `1` to disable file checkpointing. The `/rewind` command will not be able to restore code changes. Overrides the `fileCheckpointingEnabled` setting
