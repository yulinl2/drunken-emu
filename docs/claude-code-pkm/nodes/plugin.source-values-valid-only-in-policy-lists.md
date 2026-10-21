---
id: plugin.source-values-valid-only-in-policy-lists
kind: plugin
status: VERIFIED
title: "Source values valid only in policy lists"
sources: [S51]
---

# Source values valid only in policy lists

**Sources:** [S51](src.s51.md)

`hostPattern`, `pathPattern`, `skills-dir`, and the `owner/*` form of `repo` are valid only in the two policy lists, `strictKnownMarketplaces` and `blockedMarketplaces`:
