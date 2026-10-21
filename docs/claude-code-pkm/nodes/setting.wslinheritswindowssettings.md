---
id: setting.wslinheritswindowssettings
kind: setting
status: VERIFIED
title: "wslInheritsWindowsSettings"
sources: [S61]
---

# wslInheritsWindowsSettings

**Sources:** [S61](src.s61.md)

When set in the HKLM registry or a file under `C:\Program Files\ClaudeCode`, have WSL read the Windows policy chain, and read `/etc/claude-code` only when no Windows admin document is present; the entry gives the order
