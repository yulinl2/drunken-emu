---
id: feature.otel-log-managed-settings
kind: feature
status: VERIFIED
title: "OTEL_LOG_MANAGED_SETTINGS"
sources: [S65]
---

# OTEL_LOG_MANAGED_SETTINGS

**Sources:** [S65](src.s65.md)

Add the redacted managed settings, and a SHA-256 digest of the settings before redaction, to managed settings resolved events (default: disabled). A value in project or local settings doesn't turn it on. Requires Claude Code v2.1.274 or later (example values: `1` to enable)
