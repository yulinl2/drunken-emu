---
id: feature.which-managed-settings-sources-a-machine-runs-on-whether-its
kind: feature
status: VERIFIED
title: "Which managed settings sources a machine runs on, whether its policy helper is healthy, and why a machine refused to start"
sources: [S65]
---

# Which managed settings sources a machine runs on, whether its policy helper is healthy, and why a machine refused to start

**Sources:** [S65](src.s65.md)

event: `managed_settings_resolved`; key attributes: `managed_settings.trigger`, `managed_settings.sources`, `managed_settings.source_behavior`, `managed_settings.helper.state`, `error.type`; `managed_settings.settings` and `managed_settings.resolved_sha256` with `OTEL_LOG_MANAGED_SETTINGS=1`
