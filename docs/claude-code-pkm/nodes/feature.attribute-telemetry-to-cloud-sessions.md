---
id: feature.attribute-telemetry-to-cloud-sessions
kind: feature
status: VERIFIED
title: "Attribute telemetry to cloud sessions"
sources: [S65]
---

# Attribute telemetry to cloud sessions

**Sources:** [S65](src.s65.md)

By default, metrics and events from a cloud session carry the standard attributes, including `session.id`, `ccr.session.id`, and `organization.id`, so you can filter by session or organization without extra configuration. The `ccr.session.id` value is the session's `CLAUDE_CODE_REMOTE_SESSION_ID`. To turn it into the session's transcript URL, see Link output back to the session.
