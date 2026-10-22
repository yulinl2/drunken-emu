---
id: env.enable-beta-tracing-detailed
kind: env
status: VERIFIED
title: "ENABLE_BETA_TRACING_DETAILED"
sources: [S81]
---

# ENABLE_BETA_TRACING_DETAILED

**Sources:** [S81](src.s81.md)

Set to `1`, and set `BETA_TRACING_ENDPOINT` to your OTLP/HTTP collector endpoint, to turn on detailed beta tracing, which adds content-bearing span attributes and the `claude_code.hook` span. Interactive CLI sessions also require your organization to be allowlisted for the beta. Both variables are ignored in project and local settings
