---
id: feature.fallback-model-chains
kind: feature
status: VERIFIED
title: "Fallback model chains"
sources: [S70]
---

# Fallback model chains

**Sources:** [S70](src.s70.md)

When the primary model is overloaded, unavailable, or returns another non-retryable server error, Claude Code can switch to a fallback model instead of failing the request. Authentication, billing, rate-limit, request-size, and transport errors, and a denial by your organization's policy check, never trigger a switch; those follow their normal retry and error handling. It does switch when Amazon B
