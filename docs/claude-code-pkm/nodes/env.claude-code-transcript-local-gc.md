---
id: env.claude-code-transcript-local-gc
kind: env
status: VERIFIED
title: "CLAUDE_CODE_TRANSCRIPT_LOCAL_GC"
sources: [S81]
---

# CLAUDE_CODE_TRANSCRIPT_LOCAL_GC

**Sources:** [S81](src.s81.md)

Set to `1` to limit how large the transcript file of a long `-p` or Agent SDK session grows. After each compaction, once the file is larger than 5 MB, Claude Code removes the history from before that compaction. On v2.1.296 or later, the file stays as it is when removing that history would shrink it by less than 10%. Resuming the session restores the same conversation whether or not the file was trimmed. Set it in the environment you start Claude Code from, since a settings `env` block can't turn it on. Requires Claude Code v2.1.287 or later
