---
id: plugin.marketplace-file
kind: plugin
status: VERIFIED
title: "Marketplace file"
sources: [S51]
---

# Marketplace file

**Sources:** [S51](src.s51.md)

Save the marketplace file at `.claude-plugin/marketplace.json` in your marketplace's directory. If you keep the file somewhere else in the repository, users have to declare the marketplace in `extraKnownMarketplaces` with `path` set on its source, because `claude plugin marketplace add` has no option for it.
