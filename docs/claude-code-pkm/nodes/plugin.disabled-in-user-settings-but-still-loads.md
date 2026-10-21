---
id: plugin.disabled-in-user-settings-but-still-loads
kind: plugin
status: VERIFIED
title: "Disabled in user settings but still loads"
sources: [S49]
---

# Disabled in user settings but still loads

**Sources:** [S49](src.s49.md)

If you set a plugin to `false` in `~/.claude/settings.json` and it still loads, a `true` in a higher-precedence source is overriding it. The plugin's row in `claude plugin list` and in `/plugin` shows `Disabled in ~/.claude/settings.json but still loads — project settings enable it, which overrides your user setting`. The message names the source that overrode you: `project`, `project, gitignored`
