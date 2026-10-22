---
id: plugin.restrict-what-users-can-install
kind: plugin
status: VERIFIED
title: "Restrict what users can install"
sources: [S59]
---

# Restrict what users can install

**Sources:** [S59](src.s59.md)

The managed `strictKnownMarketplaces` allowlist and `blockedMarketplaces` blocklist decide which marketplace sources plugins may come from. A marketplace's source is the git repository, URL, or local path that Claude Code fetches it from. Both lists match the source of the marketplace a plugin comes from, not the plugin's own entry inside that marketplace.
