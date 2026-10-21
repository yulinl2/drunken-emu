---
id: setting.strictknownmarketplaces
kind: setting
status: VERIFIED
title: "strictKnownMarketplaces"
sources: [S61]
---

# strictKnownMarketplaces

**Sources:** [S61](src.s61.md)

Enforced as an empty allowlist until the value is fixed, so no marketplace source is admitted. An individual entry that is invalid or can't be enforced, such as a `hostPattern` regex that doesn't compile, is stripped and the valid subset is enforced.
