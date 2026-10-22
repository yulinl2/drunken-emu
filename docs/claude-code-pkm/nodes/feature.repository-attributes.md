---
id: feature.repository-attributes
kind: feature
status: VERIFIED
title: "Repository attributes"
sources: [S65]
---

# Repository attributes

**Sources:** [S65](src.s65.md)

Set `OTEL_METRICS_INCLUDE_REPOSITORY=true` to tag metrics and events with the identity of the session's repository, so a shared collector can attribute usage per repository. Requires Claude Code v2.1.269 or later.
