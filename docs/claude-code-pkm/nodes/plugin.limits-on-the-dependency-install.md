---
id: plugin.limits-on-the-dependency-install
kind: plugin
status: VERIFIED
title: "Limits on the dependency install"
sources: [S49]
---

# Limits on the dependency install

**Sources:** [S49](src.s49.md)

Claude Code constrains this dependency install so that no code from the plugin or its packages executes during it, and bounds how long it can run:
