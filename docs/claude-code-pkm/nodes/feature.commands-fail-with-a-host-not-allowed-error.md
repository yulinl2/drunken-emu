---
id: feature.commands-fail-with-a-host-not-allowed-error
kind: feature
status: VERIFIED
title: "Commands fail with a host-not-allowed error"
sources: [S68]
---

# Commands fail with a host-not-allowed error

**Sources:** [S68](src.s68.md)

Many CLI tools need to reach specific hosts. Approve the host when prompted, or add it to `allowedDomains`. If your organization locks the allowlist with `allowManagedDomainsOnly`, there's no prompt, so ask your administrator to add the host.
