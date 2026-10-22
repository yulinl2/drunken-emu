---
id: plugin.hooks-in-an-entry
kind: plugin
status: VERIFIED
title: "Hooks in an entry"
sources: [S51]
---

# Hooks in an entry

**Sources:** [S51](src.s51.md)

Write entry `hooks` as an inline object that maps hook event names to matcher arrays. If you write a file path or an array instead, `claude plugin validate` passes it. Those hooks never run, and Claude Code reports a `not yet supported in a marketplace entry` error for the plugin. Put file-based hooks in the plugin's own `hooks/hooks.json` or `plugin.json`.
