---
id: feature.hosts-outside-your-allowed-domains
kind: feature
status: VERIFIED
title: "Hosts outside your allowed domains"
sources: [S68]
---

# Hosts outside your allowed domains

**Sources:** [S68](src.s68.md)

When a sandboxed command connects to a host that isn't in your allowed domains, the command stays in the sandbox and waits for a decision. In an interactive terminal session, the decision depends on your permission mode:
