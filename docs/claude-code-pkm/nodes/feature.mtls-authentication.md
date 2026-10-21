---
id: feature.mtls-authentication
kind: feature
status: VERIFIED
title: "mTLS authentication"
sources: [S65]
---

# mTLS authentication

**Sources:** [S65](src.s65.md)

How you configure client certificates for the OTLP exporter depends on the OTLP protocol in use for that signal, set via `OTEL_EXPORTER_OTLP_PROTOCOL` or the per-signal override. The same configuration applies to metrics, logs, and traces.
