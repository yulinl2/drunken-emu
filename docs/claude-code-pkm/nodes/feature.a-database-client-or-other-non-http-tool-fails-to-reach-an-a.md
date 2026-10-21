---
id: feature.a-database-client-or-other-non-http-tool-fails-to-reach-an-a
kind: feature
status: VERIFIED
title: "A database client or other non-HTTP tool fails to reach an allowed host"
sources: [S68]
---

# A database client or other non-HTTP tool fails to reach an allowed host

**Sources:** [S68](src.s68.md)

A tool that ignores the proxy environment variables can't connect from inside the sandbox, even to a host in `allowedDomains`. A sandboxed command has no direct route to the network, so a tool that opens its own connection fails. Most database drivers, plain `ssh`, and tools that use UDP behave this way.
