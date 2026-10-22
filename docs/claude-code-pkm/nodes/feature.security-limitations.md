---
id: feature.security-limitations
kind: feature
status: VERIFIED
title: "Security limitations"
sources: [S68]
---

# Security limitations

**Sources:** [S68](src.s68.md)

Network filtering: the sandbox restricts which domains processes can connect to. By default the built-in proxy does not terminate or inspect TLS on outbound traffic, so the contents of encrypted connections are not examined. The experimental `network.tlsTerminate` setting terminates TLS at the proxy for `mask` credential substitution but does not add content filtering. You are responsible for ensu
