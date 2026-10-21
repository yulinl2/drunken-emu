---
id: hook-rule.reload-skills-that-a-hook-installs
kind: hook-rule
status: VERIFIED
title: "Reload skills that a hook installs"
sources: [S85]
---

# Reload skills that a hook installs

**Sources:** [S85](src.s85.md)

To make skills that a SessionStart hook installs available in the same session, return `reloadSkills`. Skill discovery normally runs before SessionStart hooks finish, so without it, files a hook writes into `~/.claude/skills/` or `.claude/skills/` can be missing when the first prompt runs.
