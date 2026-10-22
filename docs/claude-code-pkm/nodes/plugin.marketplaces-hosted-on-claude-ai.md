---
id: plugin.marketplaces-hosted-on-claude-ai
kind: plugin
status: VERIFIED
title: "Marketplaces hosted on claude.ai"
sources: [S59]
---

# Marketplaces hosted on claude.ai

**Sources:** [S59](src.s59.md)

The allowlist and blocklist match a marketplace hosted on claude.ai by its host. To allow or block one, add a `hostPattern` entry that matches `claude.ai` to `strictKnownMarketplaces` or `blockedMarketplaces`. On the allowlist, such an entry admits your organization's claude.ai marketplaces and the claude.ai default marketplaces, but not a marketplace made of a member's own claude.ai uploads or on
