---
id: setting.restriction-allowlists
kind: setting
status: VERIFIED
title: "Restriction allowlists"
sources: [S61]
---

# Restriction allowlists

**Sources:** [S61](src.s61.md)

how claude code combines it: Takes the list whole from the highest-ranked source that sets it, without adding entries from lower sources; examples: `availableModels`, `allowedMcpServers`, `strictKnownMarketplaces`, `allowedChannelPlugins`, and the `fallbackModel` chain
