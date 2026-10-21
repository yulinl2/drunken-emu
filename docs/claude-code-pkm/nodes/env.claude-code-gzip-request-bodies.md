---
id: env.claude-code-gzip-request-bodies
kind: env
status: VERIFIED
title: "CLAUDE_CODE_GZIP_REQUEST_BODIES"
sources: [S81]
---

# CLAUDE_CODE_GZIP_REQUEST_BODIES

**Sources:** [S81](src.s81.md)

Set to `0` to turn off gzip compression of Claude API, telemetry, and artifact publish request bodies sent to `api.anthropic.com`. By default, Claude Code compresses large request bodies on direct connections and skips compression when you send requests through a proxy, configure a client certificate, or set `NODE_EXTRA_CA_CERTS`. Use `0` if a TLS-inspecting proxy that Claude Code can't detect mishandles compressed requests
