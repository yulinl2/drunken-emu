---
id: plugin.hooks
kind: plugin
status: VERIFIED
title: "Hooks"
sources: [S45]
---

# Hooks

**Sources:** [S45](src.s45.md)

A hook runs something automatically at a point in Claude Code's lifecycle, such as after every file edit: a shell command, an HTTP request, an MCP tool call, a prompt to a model, or a subagent. Save the plugin's hooks in `hooks/hooks.json` at the plugin root, under a top-level `"hooks"` key, in the same shape as the `hooks` object in `settings.json`. That lets you copy an existing settings hook in
