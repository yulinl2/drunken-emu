---
id: env.claude-code-cert-store
kind: env
status: VERIFIED
title: "CLAUDE_CODE_CERT_STORE"
sources: [S81]
---

# CLAUDE_CODE_CERT_STORE

**Sources:** [S81](src.s81.md)

Comma-separated list of CA certificate sources for TLS connections. `bundled` is the Mozilla CA set shipped with Claude Code. `system` is the operating system trust store, read only on runtimes with `tls.getCACertificates`: the native binary, or Node 22.15 or later for npm installs. See CA certificate store. Default is `bundled,system`
