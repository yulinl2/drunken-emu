---
id: feature.app-entrypoint
kind: feature
status: VERIFIED
title: "app.entrypoint"
sources: [S65]
---

# app.entrypoint

**Sources:** [S65](src.s65.md)

How the session was launched, such as `cli`, `sdk-cli`, `sdk-ts`, `sdk-py`, `claude-vscode`, or `claude-in-slack` for Claude Tag sessions (controlled by: `OTEL_METRICS_INCLUDE_ENTRYPOINT` (default: false))
