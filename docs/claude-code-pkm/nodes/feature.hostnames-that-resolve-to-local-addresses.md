---
id: feature.hostnames-that-resolve-to-local-addresses
kind: feature
status: VERIFIED
title: "Hostnames that resolve to local addresses"
sources: [S68]
---

# Hostnames that resolve to local addresses

**Sources:** [S68](src.s68.md)

After a hostname passes the allowlist, the sandbox proxy resolves it and refuses the connection when the name resolves only to local addresses. Local addresses include loopback addresses such as `127.0.0.1`, link-local addresses such as the `169.254.169.254` cloud metadata endpoint, and addresses assigned to your own machine. The names `localhost` and `*.localhost` are allowed to resolve to loopba
