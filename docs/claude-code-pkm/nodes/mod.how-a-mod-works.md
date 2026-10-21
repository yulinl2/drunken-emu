---
id: mod.how-a-mod-works
kind: mod
status: VERIFIED
title: "How a mod works"
sources: [S53]
---

# How a mod works

**Sources:** [S53](src.s53.md)

A mod is a plugin whose code registers event handlers, called hooks. Claude Code runs a hook when its event happens, such as when Claude calls a tool or when the spinner is drawn. A small mod has three files:
