---
id: mod.stop-user-installed-mods-from-loading
kind: mod
status: VERIFIED
title: "Stop user-installed mods from loading"
sources: [S58]
---

# Stop user-installed mods from loading

**Sources:** [S58](src.s58.md)

To keep every mod your users bring from running its hooks, set the `allowManagedModsOnly` option on the built-in guard, a policy mod that Claude Code loads ahead of every mod a user installs. The option goes in managed settings under `pluginConfigs`, keyed by `cc-plugin-sec-default@builtin`:
