---
id: feature.ipv6-addresses-in-domain-lists
kind: feature
status: VERIFIED
title: "IPv6 addresses in domain lists"
sources: [S68]
---

# IPv6 addresses in domain lists

**Sources:** [S68](src.s68.md)

To match an IPv6 address in `allowedDomains`, `deniedDomains`, or a `WebFetch(domain:...)` rule, write the address in brackets: `"[::1]"` matches that address on every port, and `"[::1]:443"` matches it on port 443 only. The bracketed form requires Claude Code v2.1.229 or later.
