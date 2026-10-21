---
id: plugin.executables
kind: plugin
status: VERIFIED
title: "Executables"
sources: [S45]
---

# Executables

**Sources:** [S45](src.s45.md)

Files in `bin/` at the plugin root are on the `PATH` of the Bash tool's shell while the plugin is enabled, so Claude can run them as bare commands. A command that Claude runs with the PowerShell tool outside the sandbox finds them on its `PATH` too, and a sandboxed PowerShell command doesn't. Add an executable script:
