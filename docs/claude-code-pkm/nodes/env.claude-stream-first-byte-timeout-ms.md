---
id: env.claude-stream-first-byte-timeout-ms
kind: env
status: VERIFIED
title: "CLAUDE_STREAM_FIRST_BYTE_TIMEOUT_MS"
sources: [S81]
---

# CLAUDE_STREAM_FIRST_BYTE_TIMEOUT_MS

**Sources:** [S81](src.s81.md)

Deadline in milliseconds for the first response byte of a streaming request, on the connections where the first-byte deadline runs. For how Claude Code clamps it, the extra time it adds for large request bodies, and how it picks the deadline when you leave this unset, see No response from API. Requires Claude Code v2.1.242 or later
