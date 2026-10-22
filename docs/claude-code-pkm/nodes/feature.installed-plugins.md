---
id: feature.installed-plugins
kind: feature
status: VERIFIED
title: "Installed plugins"
sources: [S16]
---

# Installed plugins

**Sources:** [S16](src.s16.md)

Cloned marketplaces, installed plugin versions, the `installed_plugins.json` install record, and per-plugin data, managed by `claude plugin` commands. Plugins synced from your claude.ai account download into `~/.claude/plugins/synced/`. For a plugin installed from a marketplace `command` source in link mode, Claude Code stores links here instead of a copy, and the plugin's files stay in the directory the command prints. A `command` source requires Claude Code v2.1.229 or later. A plugin listed by relative path in a marketplace you added from a local path also loads in place from its source directory rather than from a cache copy. See plugin caching for how orphaned versions are cleaned up. (location: `~/.claude/plugins`)
