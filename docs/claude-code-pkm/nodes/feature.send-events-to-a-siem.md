---
id: feature.send-events-to-a-siem
kind: feature
status: VERIFIED
title: "Send events to a SIEM"
sources: [S65]
---

# Send events to a SIEM

**Sources:** [S65](src.s65.md)

Point `OTEL_EXPORTER_OTLP_LOGS_ENDPOINT` at your SIEM's OTLP receiver, or at an OpenTelemetry Collector that forwards to your SIEM's native ingest API. The following managed-settings example exports events only, with full tool detail enabled for MCP and Bash auditing:
