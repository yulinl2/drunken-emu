---
id: setting.allowedproviders
kind: setting
status: VERIFIED
title: "allowedProviders"
sources: [S61]
---

# allowedProviders

**Sources:** [S61](src.s61.md)

Enforced as an empty allowlist until the value is fixed, so every API provider is refused and Claude Code doesn't start on the machine. If only an individual entry isn't a known provider name, Claude Code drops and reports that entry and enforces the rest.
