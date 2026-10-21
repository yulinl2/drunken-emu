---
id: plugin.require-a-marketplace-and-its-plugins
kind: plugin
status: VERIFIED
title: "Require a marketplace and its plugins"
sources: [S59]
---

# Require a marketplace and its plugins

**Sources:** [S59](src.s59.md)

Add the marketplace under `extraKnownMarketplaces`, keyed by the marketplace's own `name` from its `marketplace.json`. Then add each plugin under `enabledPlugins` as `plugin-name@marketplace-name`. Each marketplace entry carries a `source` object with a `source` field naming the type, such as `github`. This managed settings example registers an organization marketplace and force-enables two plugin
