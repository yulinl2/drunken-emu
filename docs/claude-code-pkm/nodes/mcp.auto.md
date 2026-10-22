---
id: mcp.auto
kind: mcp
status: VERIFIED
title: "auto"
sources: [S31]
---

# auto

**Sources:** [S31](src.s31.md)

Threshold mode. Tools that would otherwise be deferred load upfront while their definitions total under 10% of the context window. At 10% or more, tool search turns on, and those tools can stay deferred even if the total falls under 10%
