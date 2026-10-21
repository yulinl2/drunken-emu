---
id: plugin.when-a-command-source-re-runs
kind: plugin
status: VERIFIED
title: "When a command source re-runs"
sources: [S49]
---

# When a command source re-runs

**Sources:** [S49](src.s49.md)

Plugins with a `command` source don't wait for the auto-update pass. The printed directory reflects the tool's state at the time the command ran, so Claude Code runs the command you accepted again at these times:
