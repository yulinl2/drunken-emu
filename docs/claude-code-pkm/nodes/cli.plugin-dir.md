---
id: cli.plugin-dir
kind: cli
status: VERIFIED
title: "--plugin-dir"
sources: [S52]
---

# --plugin-dir

**Sources:** [S52](src.s52.md)

Load a plugin from a directory or a `.zip` archive of one. A folder of plugins loads each child folder that holds a `.claude-plugin/plugin.json`. Each flag takes one path (example: `claude --plugin-dir ./my-plugin --plugin-dir ./other.zip`)
