---
id: cli.config
kind: cli
status: VERIFIED
title: "--config"
sources: [S52]
---

# --config

**Sources:** [S52](src.s52.md)

Set a `userConfig` option the plugin's manifest declares. Repeat the flag for each option. A key written `.` sets a setting that a bundled MCP server declares in its own `user_config` instead, for a bundle file shipped inside the plugin. The `.` form requires Claude Code v2.1.285 or later
