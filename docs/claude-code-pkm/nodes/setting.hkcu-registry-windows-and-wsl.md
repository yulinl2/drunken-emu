---
id: setting.hkcu-registry-windows-and-wsl
kind: setting
status: VERIFIED
title: "HKCU registry, Windows and WSL"
sources: [S61]
---

# HKCU registry, Windows and WSL

**Sources:** [S61](src.s61.md)

how you deliver it: As a Windows `HKCU` registry value; see where each mechanism stores the policy; when claude code reads it: Read at startup and checked for changes every 30 minutes; Claude Code uses it only when no admin document is present above it and no host-supplied parent settings supply a restrictive key; use it when: You can't write the machine-level `HKLM` key
