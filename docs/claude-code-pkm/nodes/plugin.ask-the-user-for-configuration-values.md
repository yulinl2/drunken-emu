---
id: plugin.ask-the-user-for-configuration-values
kind: plugin
status: VERIFIED
title: "Ask the user for configuration values"
sources: [S45]
---

# Ask the user for configuration values

**Sources:** [S45](src.s45.md)

Declare the values your plugin needs from the user in the `userConfig` manifest key, so users don't edit `settings.json` themselves. Each option appears in a dialog with its `title` as the label and its `description` beneath it.
