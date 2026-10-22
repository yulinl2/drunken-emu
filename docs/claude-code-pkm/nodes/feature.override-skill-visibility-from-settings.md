---
id: feature.override-skill-visibility-from-settings
kind: feature
status: VERIFIED
title: "Override skill visibility from settings"
sources: [S32]
---

# Override skill visibility from settings

**Sources:** [S32](src.s32.md)

The `skillOverrides` setting controls skill visibility from your settings instead of the skill's own frontmatter. Use it for skills whose SKILL.md you don't want to edit, such as ones checked into a shared project repo. The `/skills` menu writes it for you: highlight a skill and press `Space` to cycle states, then `Esc` to save to `.claude/settings.local.json`.
