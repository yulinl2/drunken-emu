---
id: plugin.command-plugin-source
kind: plugin
status: VERIFIED
title: "command plugin source"
sources: [S51]
---

# command plugin source

**Sources:** [S51](src.s51.md)

Use a `command` source when a tool installed on the user's machine produces the plugin directory, such as an IDE that renders its plugin for the toolchain the user has selected. Claude Code runs the command when the user installs or updates the plugin, and again once per session, so users get the tool's changed output without reinstalling.
