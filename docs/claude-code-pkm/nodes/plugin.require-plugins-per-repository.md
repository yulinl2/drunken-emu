---
id: plugin.require-plugins-per-repository
kind: plugin
status: VERIFIED
title: "Require plugins per repository"
sources: [S59]
---

# Require plugins per repository

**Sources:** [S59](src.s59.md)

To cover one repository's contributors instead of your whole fleet, set `extraKnownMarketplaces` and `enabledPlugins` in that repository's `.claude/settings.json`. The `extraKnownMarketplaces` entries apply only in a folder the contributor has trusted, and in an untrusted folder Claude Code ignores them without a message:
