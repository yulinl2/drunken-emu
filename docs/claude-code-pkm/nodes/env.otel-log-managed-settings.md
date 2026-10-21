---
id: env.otel-log-managed-settings
kind: env
status: VERIFIED
title: "OTEL_LOG_MANAGED_SETTINGS"
sources: [S81]
---

# OTEL_LOG_MANAGED_SETTINGS

**Sources:** [S81](src.s81.md)

Set to `1` to add the redacted managed settings, and a SHA-256 digest of the settings before redaction, to `managed_settings_resolved` OpenTelemetry log events. Disabled by default. Set it in your shell, user settings, or managed settings; a value in project or local settings doesn't turn it on. Requires Claude Code v2.1.274 or later. See Monitoring
