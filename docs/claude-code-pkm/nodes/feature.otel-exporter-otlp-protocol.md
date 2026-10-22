---
id: feature.otel-exporter-otlp-protocol
kind: feature
status: VERIFIED
title: "OTEL_EXPORTER_OTLP_PROTOCOL"
sources: [S65]
---

# OTEL_EXPORTER_OTLP_PROTOCOL

**Sources:** [S65](src.s65.md)

Protocol for OTLP exporter, applies to all signals. Claude Code has no default protocol, so set this or the signal-specific protocol variable for each `otlp` exporter you enable (example values: `grpc`, `http/json`, `http/protobuf`)
