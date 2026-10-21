---
id: mod.where-mods-run
kind: mod
status: VERIFIED
title: "Where mods run"
sources: [S53]
---

# Where mods run

**Sources:** [S53](src.s53.md)

A mod's hooks run in every kind of session that loads the plugin, whichever provider serves the model, including Amazon Bedrock, Google Cloud's Agent Platform, and Microsoft Foundry. Drawing is narrower: what a mod draws appears in the terminal, the Desktop app, and the VS Code extension. This table lists each place you might run Claude Code:
