---
id: env.otel-metrics-include-repository
kind: env
status: VERIFIED
title: "OTEL_METRICS_INCLUDE_REPOSITORY"
sources: [S81]
---

# OTEL_METRICS_INCLUDE_REPOSITORY

**Sources:** [S81](src.s81.md)

Set to `true` to tag OpenTelemetry metrics and events with `vcs.*` attributes identifying the session's repository (default: excluded). Requires Claude Code v2.1.269 or later. See Repository attributes
