---
id: plugin-field.executables
kind: plugin-field
status: VERIFIED
title: "Executables"
sources: [S50]
---

# Executables

**Sources:** [S50](src.s50.md)

default location: `bin/`; contents: Files here are on the Bash tool's `PATH` while the plugin is enabled, so Claude runs them as bare commands. claude.ai and Cowork don't install a plugin that has this directory, including one you distribute through claude.ai organization settings
