---
id: plugin.commands-plugins-manifest-reference
kind: plugin
status: VERIFIED
title: "commands"
sources: [S50]
---

# commands

**Sources:** [S50](src.s50.md)

`commands` takes a path, an array of paths, or an object map. A path names a flat `.md` command file or a directory. In the object map, each key becomes the command name after the plugin prefix. For example, `"about"` in plugin `deploy-tools` runs as `/deploy-tools:about`.
