---
id: env.claude-code-otel-diag-stderr
kind: env
status: VERIFIED
title: "CLAUDE_CODE_OTEL_DIAG_STDERR"
sources: [S81]
---

# CLAUDE_CODE_OTEL_DIAG_STDERR

**Sources:** [S81](src.s81.md)

Set to `1` to write OpenTelemetry exporter diagnostic errors to stderr. By default these errors only appear with `--debug`, so a misconfigured exporter such as a Prometheus port collision otherwise fails silently. Requires Claude Code v2.1.179 or later. See Monitoring
