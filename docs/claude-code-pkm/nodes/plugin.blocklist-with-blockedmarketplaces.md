---
id: plugin.blocklist-with-blockedmarketplaces
kind: plugin
status: VERIFIED
title: "Blocklist with blockedMarketplaces"
sources: [S59]
---

# Blocklist with blockedMarketplaces

**Sources:** [S59](src.s59.md)

`blockedMarketplaces` takes the same source objects as `strictKnownMarketplaces` and is checked first, so a source on both lists is blocked. Blocklist matching is wider than allowlist matching:
