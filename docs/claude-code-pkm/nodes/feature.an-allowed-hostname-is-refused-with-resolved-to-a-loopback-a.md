---
id: feature.an-allowed-hostname-is-refused-with-resolved-to-a-loopback-a
kind: feature
status: VERIFIED
title: "An allowed hostname is refused with resolved to a loopback address"
sources: [S68]
---

# An allowed hostname is refused with resolved to a loopback address

**Sources:** [S68](src.s68.md)

The sandbox proxy refuses an allowed hostname that resolves to a local address, which affects development names such as `myapp.test` that point at `127.0.0.1`. The command sees a `403` response whose body names the kind of address, such as `Connection to myapp.test blocked: resolved to a loopback address`.
