---
id: feature.hook-never-fires-debug-your-config-3
kind: feature
status: VERIFIED
title: "Hook never fires"
sources: [S40]
---

# Hook never fires

**Sources:** [S40](src.s40.md)

cause: Hooks are defined in a standalone file instead of `settings.json`; fix: There is no standalone hooks file for project or user config. Define hooks under the `"hooks"` key in `settings.json`. Only plugins load a separate `hooks/hooks.json`. See hook configuration.
