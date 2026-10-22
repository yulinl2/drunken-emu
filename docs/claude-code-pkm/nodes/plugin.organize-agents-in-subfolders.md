---
id: plugin.organize-agents-in-subfolders
kind: plugin
status: VERIFIED
title: "Organize agents in subfolders"
sources: [S45]
---

# Organize agents in subfolders

**Sources:** [S45](src.s45.md)

You can put plugin agent files in subfolders of `agents/`. Claude Code loads them recursively and joins the plugin name, each subfolder name, and the file name with colons to form the agent's scoped name. For example, `agents/review/security.md` in a plugin named `my-plugin` loads as `my-plugin:review:security`. Two settings change that name:
