---
id: plugin.install-dependencies-into-the-data-directory
kind: plugin
status: VERIFIED
title: "Install dependencies into the data directory"
sources: [S45]
---

# Install dependencies into the data directory

**Sources:** [S45](src.s45.md)

For a marketplace-installed plugin, Claude Code installs eligible Node.js package dependencies automatically when it caches the plugin, so you may not need to install them yourself. When you do, this `SessionStart` hook installs `node_modules` into `${CLAUDE_PLUGIN_DATA}` on first run and again after an update changes `package.json`:
