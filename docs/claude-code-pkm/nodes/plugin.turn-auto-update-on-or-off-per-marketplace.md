---
id: plugin.turn-auto-update-on-or-off-per-marketplace
kind: plugin
status: VERIFIED
title: "Turn auto-update on or off per marketplace"
sources: [S59]
---

# Turn auto-update on or off per marketplace

**Sources:** [S59](src.s59.md)

Plugin auto-update runs in the background after startup for marketplaces that have it turned on. For which marketplaces have it on by default, see When auto-update runs. To decide for the fleet, set `"autoUpdate": true` or `false` on a managed `extraKnownMarketplaces` entry:
