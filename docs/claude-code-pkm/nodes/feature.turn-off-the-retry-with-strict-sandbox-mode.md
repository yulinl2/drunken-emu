---
id: feature.turn-off-the-retry-with-strict-sandbox-mode
kind: feature
status: VERIFIED
title: "Turn off the retry with strict sandbox mode"
sources: [S68]
---

# Turn off the retry with strict sandbox mode

**Sources:** [S68](src.s68.md)

You can disable the unsandboxed retry by setting `"allowUnsandboxedCommands": false` in your sandbox settings. With the retry disabled, Claude Code ignores the `dangerouslyDisableSandbox` parameter. While the sandbox is running, commands Claude runs are then sandboxed unless they match an `excludedCommands` entry. To keep Claude Code from running commands unsandboxed when the sandbox can't start,
