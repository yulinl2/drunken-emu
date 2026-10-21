---
id: plugin.analytics-api
kind: plugin
status: VERIFIED
title: "Analytics API"
sources: [S59]
---

# Analytics API

**Sources:** [S59](src.s59.md)

On the Enterprise plan, `GET /v1/organizations/analytics/plugins` returns per-plugin, per-day install and invocation counts across Claude Code and Cowork. You can group the counts by user or RBAC group. Plugin activity that reaches Anthropic without a plugin name appears in one aggregate `third-party` row. See the endpoint reference and Access data programmatically for the key it needs.
