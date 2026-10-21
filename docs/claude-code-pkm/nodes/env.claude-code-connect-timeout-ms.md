---
id: env.claude-code-connect-timeout-ms
kind: env
status: VERIFIED
title: "CLAUDE_CODE_CONNECT_TIMEOUT_MS"
sources: [S81]
---

# CLAUDE_CODE_CONNECT_TIMEOUT_MS

**Sources:** [S81](src.s81.md)

Removed in v2.1.186 and now a no-op. Previously set a separate timeout for the connect, TLS, and response-header phase of a streaming API request. Use `API_TIMEOUT_MS` instead. For the response-header phase of a streaming request, see `CLAUDE_STREAM_FIRST_BYTE_TIMEOUT_MS`
