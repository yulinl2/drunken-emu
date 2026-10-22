---
id: plugin.identify-anthropic-s-marketplaces-by-name
kind: plugin
status: VERIFIED
title: "Identify Anthropic's marketplaces by name"
sources: [S44]
---

# Identify Anthropic's marketplaces by name

**Sources:** [S44](src.s44.md)

A marketplace's name places it in one of three tiers: official, community, or third-party. Claude Code accepts the official and community names only for marketplaces sourced from `github.com/anthropics/` repositories, so a third-party marketplace can't present itself as an Anthropic one. A marketplace that a coworker or your organization publishes is third-party.
