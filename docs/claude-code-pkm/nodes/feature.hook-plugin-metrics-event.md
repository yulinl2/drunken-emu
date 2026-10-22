---
id: feature.hook-plugin-metrics-event
kind: feature
status: VERIFIED
title: "Hook plugin metrics event"
sources: [S65]
---

# Hook plugin metrics event

**Sources:** [S65](src.s65.md)

Logged when an official-marketplace plugin hook emits per-invocation metrics. Only plugins installed from an official Anthropic marketplace can emit these. Third-party marketplace plugins and user-configured hooks don't emit to this event. Use this event to monitor plugin behavior such as finding rates, costs, and durations from your own observability stack.
