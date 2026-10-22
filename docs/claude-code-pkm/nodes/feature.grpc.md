---
id: feature.grpc
kind: feature
status: VERIFIED
title: "grpc"
sources: [S65]
---

# grpc

**Sources:** [S65](src.s65.md)

client certificate variables: `OTEL_EXPORTER_OTLP_CLIENT_KEY` and `OTEL_EXPORTER_OTLP_CLIENT_CERTIFICATE`, or the per-signal variants such as `OTEL_EXPORTER_OTLP_METRICS_CLIENT_KEY` to use a different certificate per signal; trust the collector's ca with: `OTEL_EXPORTER_OTLP_CERTIFICATE`
