---
id: cli.plugin-list-enabled-disabled
kind: cli
status: VERIFIED
title: "/plugin list [--enabled/--disabled]"
sources: [S52]
---

# /plugin list [--enabled/--disabled]

**Sources:** [S52](src.s52.md)

Prints your marketplace-installed plugins inline, with version, scope, and status. A filter flag shows only that state. A plugin whose enable state hasn't been applied yet is marked `— run /reload-plugins to apply` (aliases: `ls`)
