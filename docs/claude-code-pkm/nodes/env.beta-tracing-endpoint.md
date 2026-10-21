---
id: env.beta-tracing-endpoint
kind: env
status: VERIFIED
title: "BETA_TRACING_ENDPOINT"
sources: [S81]
---

# BETA_TRACING_ENDPOINT

**Sources:** [S81](src.s81.md)

OTLP/HTTP endpoint for detailed beta tracing: with `ENABLE_BETA_TRACING_DETAILED=1`, logs and traces go there instead of to the configured exporters. Set it in your shell, user settings, or managed settings. Ignored in project and local settings
