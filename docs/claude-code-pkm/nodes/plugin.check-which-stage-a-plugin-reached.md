---
id: plugin.check-which-stage-a-plugin-reached
kind: plugin
status: VERIFIED
title: "Check which stage a plugin reached"
sources: [S49]
---

# Check which stage a plugin reached

**Sources:** [S49](src.s49.md)

An `enabledPlugins` entry becomes a plugin you can use in stages: your settings declare it, Claude Code fetches it to disk, and the running session loads it. When a plugin doesn't behave as a settings file suggests, check which stage it reached:
