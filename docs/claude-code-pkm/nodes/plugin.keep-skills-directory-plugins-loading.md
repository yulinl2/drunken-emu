---
id: plugin.keep-skills-directory-plugins-loading
kind: plugin
status: VERIFIED
title: "Keep skills-directory plugins loading"
sources: [S59]
---

# Keep skills-directory plugins loading

**Sources:** [S59](src.s59.md)

Skills-directory plugins are the plugins users keep under `~/.claude/skills/` or a project's `.claude/skills/` in folders that carry a `.claude-plugin/plugin.json`. If you set any allowlist without a `{ "source": "skills-dir" }` entry, they stop loading. Plain skills, meaning a `SKILL.md` without that manifest, keep loading.
