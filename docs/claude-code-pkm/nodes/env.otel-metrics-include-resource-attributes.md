---
id: env.otel-metrics-include-resource-attributes
kind: env
status: VERIFIED
title: "OTEL_METRICS_INCLUDE_RESOURCE_ATTRIBUTES"
sources: [S81]
---

# OTEL_METRICS_INCLUDE_RESOURCE_ATTRIBUTES

**Sources:** [S81](src.s81.md)

As of v2.1.161, Claude Code attaches `OTEL_RESOURCE_ATTRIBUTES` keys to metric datapoint labels. Set to `false` to exclude them (default: included). See Monitoring
