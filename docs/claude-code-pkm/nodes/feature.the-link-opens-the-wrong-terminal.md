---
id: feature.the-link-opens-the-wrong-terminal
kind: feature
status: VERIFIED
title: "The link opens the wrong terminal"
sources: [S39]
---

# The link opens the wrong terminal

**Sources:** [S39](src.s39.md)

On macOS, start `claude` in your preferred terminal once and the next deep link will use it. On Linux, set the `$TERMINAL` environment variable to your preferred emulator's command name. On Windows, the order is fixed: install Windows Terminal if you want links to open there instead of a PowerShell or `cmd.exe` window.
