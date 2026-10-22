---
id: feature.managed-settings-resolved-event
kind: feature
status: VERIFIED
title: "Managed settings resolved event"
sources: [S65]
---

# Managed settings resolved event

**Sources:** [S65](src.s65.md)

Logged with the managed settings a session resolved: once at session start, again when either the managed settings or the policy helper's state changes during the session, and when Claude Code refuses to start or ends the session for one of the reasons the `error.type` attribute lists.
