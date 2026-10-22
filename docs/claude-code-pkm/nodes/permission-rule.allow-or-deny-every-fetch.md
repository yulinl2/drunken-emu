---
id: permission-rule.allow-or-deny-every-fetch
kind: permission-rule
status: VERIFIED
title: "Allow or deny every fetch"
sources: [S66]
---

# Allow or deny every fetch

**Sources:** [S66](src.s66.md)

A bare `WebFetch` rule is the tool name with no `domain:` part, such as `"deny": ["WebFetch"]`. Both it and `WebFetch(domain:*)` cover every URL, but Claude Code applies them differently, and only the `domain:` form also adds its domain to the sandbox's allowed or denied domain list. That section lists the wildcard forms the sandbox honors and the version that added bare `*`.
