---
id: feature.dynamic-headers
kind: feature
status: VERIFIED
title: "Dynamic headers"
sources: [S65]
---

# Dynamic headers

**Sources:** [S65](src.s65.md)

For enterprise environments that require dynamic authentication, you can configure a script to generate headers dynamically. Dynamic headers apply only to the `http/protobuf` and `http/json` protocols. With the `grpc` protocol, Claude Code uses only the static headers variables, `OTEL_EXPORTER_OTLP_HEADERS` and its per-signal variants.
