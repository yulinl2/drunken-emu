---
id: plugin.define-commands-in-the-manifest
kind: plugin
status: VERIFIED
title: "Define commands in the manifest"
sources: [S45]
---

# Define commands in the manifest

**Sources:** [S45](src.s45.md)

You only need this if you want to keep command files somewhere other than `commands/`, or to define a short command inside `plugin.json` without a separate Markdown file. Set the `commands` manifest key, and Claude Code reads it instead of scanning `commands/`. The key takes a path, an array of paths, or an object that maps each command name to either a `source` file or inline `content`.
