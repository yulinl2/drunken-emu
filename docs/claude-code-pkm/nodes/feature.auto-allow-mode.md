---
id: feature.auto-allow-mode
kind: feature
status: VERIFIED
title: "Auto-allow mode"
sources: [S68]
---

# Auto-allow mode

**Sources:** [S68](src.s68.md)

Claude Code approves a command automatically, with no prompt, when the command runs inside the sandbox. A command goes through the regular permission flow when it runs outside the sandbox because it matches `excludedCommands` or because Claude retries it unsandboxed.
