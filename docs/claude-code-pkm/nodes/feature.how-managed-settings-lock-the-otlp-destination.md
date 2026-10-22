---
id: feature.how-managed-settings-lock-the-otlp-destination
kind: feature
status: VERIFIED
title: "How managed settings lock the OTLP destination"
sources: [S65]
---

# How managed settings lock the OTLP destination

**Sources:** [S65](src.s65.md)

When you set an `OTEL_EXPORTER_OTLP_*` variable in managed settings, Claude Code removes conflicting developer-set variables at startup and logs a warning in the debug log. What it removes depends on which variable you set:
