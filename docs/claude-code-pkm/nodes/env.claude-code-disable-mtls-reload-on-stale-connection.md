---
id: env.claude-code-disable-mtls-reload-on-stale-connection
kind: env
status: VERIFIED
title: "CLAUDE_CODE_DISABLE_MTLS_RELOAD_ON_STALE_CONNECTION"
sources: [S81]
---

# CLAUDE_CODE_DISABLE_MTLS_RELOAD_ON_STALE_CONNECTION

**Sources:** [S81](src.s81.md)

Set to `1` to stop Claude Code from re-reading the mTLS client certificate and key when an API request fails with a connection-level error, such as a connection reset or a TLS handshake error. With the reload disabled, Claude Code loads rotated files only when it next applies settings or at the next startup. Requires Claude Code v2.1.232 or later
