---
id: plugin.where-values-are-stored
kind: plugin
status: VERIFIED
title: "Where values are stored"
sources: [S50]
---

# Where values are stored

**Sources:** [S50](src.s50.md)

Non-sensitive values are saved under `pluginConfigs` in the user's `settings.json`. Sensitive values go to the platform's secure credential store instead. The settings page lists which settings files `pluginConfigs` is read from.
