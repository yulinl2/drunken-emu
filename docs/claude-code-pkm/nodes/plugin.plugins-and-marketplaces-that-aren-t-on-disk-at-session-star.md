---
id: plugin.plugins-and-marketplaces-that-aren-t-on-disk-at-session-star
kind: plugin
status: VERIFIED
title: "Plugins and marketplaces that aren't on disk at session start"
sources: [S49]
---

# Plugins and marketplaces that aren't on disk at session start

**Sources:** [S49](src.s49.md)

Plugins load at session start from `installed_plugins.json` and the cache without using the network. After the session starts, Claude Code checks the declared marketplaces in the background:
